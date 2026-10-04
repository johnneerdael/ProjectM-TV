"""Lower native shader trees to typed, source-derived field expressions.

This first lowering preserves operation order, branches and sampling history.
Unknown nodes remain in the result. It is not yet a complete shader interpreter
or appearance predictor, and it never consumes rendered images.
"""
from dataclasses import dataclass,field
import re
from sampling_policy import texture_settings,main_sampler_bindings


@dataclass(frozen=True)
class Field:
    op:str
    args:tuple=()
    dtype:str="float"
    detail:dict=field(default_factory=dict)


@dataclass(eq=False)
class LoopPlan:
    names:tuple
    condition:Field|None=None
    updates:dict=field(default_factory=dict)
    effects:tuple=()
    iteration_limit:int=1024


BINARY={0:"and",1:"or",2:"add",3:"subtract",4:"multiply",5:"divide",6:"remainder",
        7:"less",8:"greater",9:"less_equal",10:"greater_equal",11:"equal",12:"not_equal",
        13:"bit_and",14:"bit_or",15:"bit_xor"}
PURE={"sin","cos","tan","asin","acos","atan","atan2","abs","sqrt","rsqrt",
      "length","distance","dot","cross","reflect","normalize","pow","exp","exp2","log","log2","log10",
      "min","max","clamp","saturate","lerp","smoothstep","step","frac","floor",
      "ceil","round","trunc","sign","fmod","mul","all","any"}


class ShaderFields:
    def __init__(self,*,stage:str,frame:int,warp_reads_blur:bool,frame_wrap:float|None=None):
        if stage not in {"warp","composite"}:raise ValueError("warp or composite stage required")
        self.stage=stage;self.frame=frame;self.warp_reads_blur=warp_reads_blur
        self.environment={};self.complete=True;self.unknown=[]
        self.functions={};self.global_names=set();self.globals={};self.call_stack=[]
        self.frame_wrap=frame_wrap;self.sampler_bindings={}
        self.effects=[]
        self.sample_counter=0
        self.matrix_constructors=set()

    @staticmethod
    def coerce(value:Field,dtype:str)->Field:
        if value.dtype==dtype:return value
        op='matrix_cast' if re.fullmatch(r'float[2-4]x[2-4]',dtype) else 'cast'
        return Field(op,(value,),dtype,{'target_type':dtype})

    def collect_matrix_constructors(self,node):
        """Mirror native EnumerateMatrixCtorsNeeded's shader-wide registry."""
        if isinstance(node,list):
            for item in node:self.collect_matrix_constructors(item)
        elif isinstance(node,dict):
            if node.get('kind')=='construct' and 'x' in node.get('type',{}).get('name',''):
                self.matrix_constructors.add((node['type']['name'],tuple(a['type']['name'] for a in node.get('args',[]))))
            elif node.get('kind')=='declarations':
                for declaration in node['values']:
                    dtype=declaration['type']['name'];value=declaration['value']
                    if 'x' not in dtype or declaration['type'].get('flags',0)&4:continue
                    args=[] if value is None else value['elements'] if value.get('kind')=='aggregate' else [value]
                    types=tuple(a['type']['name'] for a in args)
                    if not any('x' in name for name in types):self.matrix_constructors.add((dtype,types))
            for value in node.values():self.collect_matrix_constructors(value)

    def matrix_constructor(self,args,dtype):
        shape=self.shape(dtype)
        if shape is None:return self.unsupported('matrix constructor type not lowered',args,dtype)
        components=sum(self.shape(a.dtype)[1] for a in args if 'x' not in a.dtype and self.shape(a.dtype))
        if components>shape[1]:return self.unsupported('overfilled native matrix constructor',args,dtype)
        return Field('matrix_constructor',args,dtype,{'lowering':'pinned GLSLGenerator::OutputMatrixCtors'})

    def initializer(self,value,dtype):
        args=value.args if value.op=='aggregate' else (value,)
        if (dtype,tuple(a.dtype for a in args)) in self.matrix_constructors:
            return self.matrix_constructor(args,dtype)
        return self.coerce(value,dtype)

    @staticmethod
    def array_type(dtype):
        match=re.fullmatch(r'(.+)\[([1-9][0-9]*)\]',dtype)
        return (match[1],int(match[2])) if match else None

    def dtype(self,type_info,*,actual=None,initializer=None):
        name=type_info['name']
        if not type_info.get('array'):return name
        size=type_info.get('array_size')
        if size is None:
            if actual is not None and self.array_type(actual.dtype):
                if self.array_type(actual.dtype)[0]==name:return actual.dtype
                self.unsupported('helper array element type mismatch');return name
            if initializer is not None and initializer.get('kind')=='aggregate':length=len(initializer['elements'])
            else:
                self.unsupported('array size is not established');return name
        else:
            try:
                from field_math import evaluate
                bound=self.expression(size)
                if bound.dtype!='int':raise ValueError('array size requires integer constant expression')
                length=int(evaluate(bound))
            except ValueError:
                self.unsupported('array size is not a resolved integer constant');return name
        if not 1<=length<=4096:
            self.unsupported('array size outside supported storage budget');return name
        return f'{name}[{length}]'

    def array_declaration(self,declaration,*,global_scope=False):
        value=declaration['value'];dtype=self.dtype(declaration['type'],initializer=value)
        layout=self.array_type(dtype)
        if layout is None:return self.unsupported('array storage size unresolved',dtype=dtype)
        element,length=layout
        if value is None:
            if global_scope and declaration['type'].get('flags',0)&4:
                return Field('input',dtype=dtype,detail={'name':declaration['name']})
            return Field('array',tuple(Field('uninitialized',dtype=element) for _ in range(length)),dtype)
        elements=value.get('elements',[value])
        # Native emits element-type[](raw expressions), with no flat grouping or
        # padding. Invalid GLSL constructor layouts must not become valid arrays.
        if len(elements)!=length or any(a['type']['name']!=element and not
                (element=='float' and a['type']['name'] in {'int','float'}) for a in elements):
            return self.unsupported('native GLSL array initializer layout mismatch',dtype=dtype)
        return Field('array',tuple(self.coerce(self.expression(a),element) for a in elements),dtype)

    def read(self,value:Field)->Field:
        pending=[value];seen=set()
        while pending:
            item=pending.pop()
            if id(item) in seen:continue
            seen.add(id(item))
            if item.op=='uninitialized':return self.unsupported('uninitialized shader value reaches a read',(value,),value.dtype)
            # Loop initialization and per-component validity are checked in the
            # execution context; an initial unknown may be assigned in its body.
            if item.op in {'loop_result','loop_slot','array','array_index','array_write'}:continue
            pending.extend(item.args)
        return value

    @staticmethod
    def shape(dtype):
        match=re.fullmatch(r'(float|int|uint|bool)([1-4])?(?:x([1-4]))?',dtype)
        if match is None:return None
        base,rows,cols=match.groups()
        return base,(int(rows)*int(cols) if cols else int(rows or 1))

    def parts(self,value):
        shape=self.shape(value.dtype)
        if shape is None:return (self.unsupported('component type not understood',dtype=value.dtype),)
        base,count=shape
        if value.op=='components':return value.args
        if value.op=='uninitialized':
            return tuple(Field('uninitialized',dtype=base,detail={**value.detail,'component':i}) for i in range(count))
        if value.op=='select':
            yes=self.parts(value.args[1]);no=self.parts(value.args[2])
            return tuple(Field('select',(value.args[0],y,n),base) for y,n in zip(yes,no))
        if value.op in {'construct','aggregate'}:
            flattened=tuple(self.coerce(part,base) for arg in value.args for part in self.parts(arg))
            if len(flattened)==1 and 'x' not in value.dtype:return flattened*count
            if len(flattened)>=count:return flattened[:count]
        if value.op=='cast':
            flattened=tuple(self.coerce(part,base) for part in self.parts(value.args[0]))
            if len(flattened)==1 and 'x' not in value.dtype:return flattened*count
            if len(flattened)>=count:return flattened[:count]
            if 'x' not in value.dtype:
                zero=Field('constant',dtype=base,detail={'value':0})
                return flattened+(zero,)*(count-len(flattened))
        if count==1:return (value,)
        if 'x' not in value.dtype:
            return tuple(Field('member',(value,),base,{'field':'xyzw'[i],'swizzle':True}) for i in range(count))
        return tuple(Field('flat_component',(value,),base,{'index':i}) for i in range(count))

    def member_indices(self,dtype,name):
        if 'x' in dtype:
            matrix=re.fullmatch(r'(?:float|int|uint|bool)([1-4])x([1-4])',dtype)
            member=re.fullmatch(r'_m([0-3])([0-3])',name)
            offset=0
            if member is None:member=re.fullmatch(r'_([1-4])([1-4])',name);offset=1
            if matrix is None or member is None:
                self.unsupported('multiple/unsupported matrix member in pinned generator');return None
            row=int(member[1])-offset;column=int(member[2])-offset
            if row>=int(matrix[1]) or column>=int(matrix[2]):
                self.unsupported('matrix member out of bounds');return None
            return [row*int(matrix[2])+column]
        shape=self.shape(dtype)
        if shape is None or any(c not in 'xyzwrgba' for c in name):
            self.unsupported('non-numeric shader member');return None
        indices=[('xyzw'.index(c) if c in 'xyzw' else 'rgba'.index(c)) if shape[1]>1 else 0 for c in name]
        if any(i>=shape[1] for i in indices):self.unsupported('vector member out of bounds');return None
        return indices

    def lower(self,tree:list[dict])->Field:
        """Lower the entry body; uniforms stay symbolic rather than guessed zero."""
        self.collect_matrix_constructors(tree)
        for node in tree:
            if node['kind']=='function':self.functions.setdefault(node['name'],[]).append(node)
            elif node['kind']=='declarations':
                for declaration in node['values']:
                    name=declaration['name'];self.global_names.add(name)
                    dtype=declaration['type']['name']
                    if declaration['type'].get('array'):
                        value=self.array_declaration(declaration,global_scope=True)
                    elif declaration['value'] is not None:value=self.initializer(self.expression(declaration['value']),dtype)
                    else:value=Field('input' if declaration['type'].get('flags',0)&4 or dtype.startswith('sampler') else 'uninitialized',dtype=dtype,detail={'name':name})
                    self.environment[name]=value
                    self.globals[name]=self.environment[name]
            else:self.unsupported('shader global not lowered: '+node['kind'])
        entries=self.functions.get('PS',[])
        samplers=[name for name in self.global_names if name.startswith('sampler_')]
        self.sampler_bindings=main_sampler_bindings(samplers,stage=self.stage,frame_wrap=self.frame_wrap)
        if len(entries)!=1:return self.unsupported('missing or ambiguous shader entry point')
        for argument in entries[0]['args']:
            # GLSL out parameters have no incoming value. Keep unwritten
            # components invalid rather than requesting a fictitious uniform.
            kind='uninitialized' if argument['modifier']==2 else 'input'
            self.environment[argument['name']]=Field(kind,dtype=argument['type']['name'],detail={'name':argument['name']})
        self.statements(entries[0]['body'])
        if 'ret' not in self.environment:return self.unsupported('missing shader result')
        result=self.environment['ret']
        if not self.complete and result.op!='unknown':
            return Field('unknown',(result,),result.dtype,{'reason':'shader contains unresolved semantic effects'})
        if self.effects:result=Field('sequence',tuple(self.effects)+(result,),result.dtype)
        return result

    def helper(self,node:dict,args:tuple,dtype:str)->Field:
        name=node['function'];candidates=self.functions[name]
        signature=node.get('signature')
        if signature is not None:
            expected=[a['type'] for a in signature]
            candidates=[f for f in candidates if [a['type'] for a in f['args']]==expected]
        if len(candidates)!=1:return self.unsupported('ambiguous shader helper: '+name,args,dtype)
        function=candidates[0];parameters=function['args'];body=function['body']
        if any(p['modifier'] in {2,3} for p in parameters):
            return self.unsupported('shader helper output arguments not lowered: '+name,args,dtype)
        if name in self.call_stack:return self.unsupported('recursive shader helper: '+name,args,dtype)
        if not body or body[-1]['kind']!='return' or any(s['kind']=='return' for s in body[:-1]):
            return self.unsupported('nonterminal shader helper return not lowered: '+name,args,dtype)
        if len(args)>len(parameters):return self.unsupported('shader helper argument count mismatch',args,dtype)
        caller=self.environment
        globals_before=dict(self.globals)
        caller_effects=self.effects;self.effects=[]
        self.environment=dict(globals_before);self.call_stack.append(name)
        try:
            for i,p in enumerate(parameters):
                value=args[i] if i<len(args) else self.expression(p.get('default'))
                self.environment[p['name']]=self.coerce(value,self.dtype(p['type'],actual=value))
            self.statements(body[:-1]);result=self.coerce(self.expression(body[-1]['value']),function['return_type']['name'])
            if self.globals!=globals_before:
                return self.unsupported('shader helper global writes not lowered: '+name,(result,),dtype)
            if self.effects:result=Field('sequence',tuple(self.effects)+(result,),result.dtype)
            return result
        finally:self.environment=caller;self.globals=globals_before;self.call_stack.pop();self.effects=caller_effects

    @staticmethod
    def has_assignment(node)->bool:
        if isinstance(node,list):return any(ShaderFields.has_assignment(n) for n in node)
        if not isinstance(node,dict):return False
        if node.get('kind')=='binary' and node['operator']>=16:return True
        if node.get('kind')=='unary' and node['operator'] in {3,4,5,6}:return True
        return any(ShaderFields.has_assignment(v) for v in node.values())

    def scoped(self,body:list[dict]):
        """Restore block declarations while preserving assignments to outer names."""
        before=dict(self.environment)
        declared={d['name'] for s in body if s['kind']=='declarations' for d in s['values']}
        self.statements(body)
        for name in declared:
            if name in before:self.environment[name]=before[name]
            else:self.environment.pop(name,None)

    def unsupported(self,reason:str,args:tuple=(),dtype:str="float")->Field:
        self.complete=False;self.unknown.append(reason)
        return Field("unknown",args,dtype,{"reason":reason})

    def texture(self,name:str,args:tuple,dtype:str)->Field:
        policy=self.sampler_bindings.get(name,texture_settings(name));base=policy['texture'].lower()
        if base=='main':
            if name not in self.sampler_bindings:
                if self.stage=='warp':
                    # Without a complete tree, earlier main aliases can change
                    # which sampler occupies overridden unit0. Keep that unknown.
                    policy={**policy,'unit':None,'wrap':None,'linear':True if name=='sampler_main' else None,
                            'binding_condition':'complete main-sampler order required'}
            source_frame=self.frame-1 if self.stage=="warp" else self.frame
            surface="pre_composite_feedback" if self.stage=="warp" else "current_warp_with_draws"
        elif name in {'sampler_blur1','sampler_blur2','sampler_blur3'}:
            source_frame=self.frame-(2 if self.stage=="warp" and self.warp_reads_blur else 1)
            surface="blur_of_pre_composite_feedback"
            policy={**policy,'wrap':False,'linear':True}
        elif base in {'blur1','blur2','blur3'}:
            return self.unsupported('prefixed blur sampler binding not established',(args[0],),dtype)
        else:
            source_frame=None;surface="procedural_or_external_texture"
        site_index=self.sample_counter;self.sample_counter+=1
        return Field("sample",args,dtype,{"sampler":name,"surface":surface,"frame":source_frame,'site_index':site_index,
            'canonical_texture':base,'sampling_policy':policy,
            "coordinate_convention":"MilkDrop shader UV; underlying main/blur flips remain explicit pipeline requirements"})

    def write(self,target:dict,value:Field):
        type_info=target.get('type',{'name':value.dtype})
        dtype=self.dtype(type_info,actual=value)
        if self.array_type(dtype) and value.dtype!=dtype:
            return self.unsupported('incompatible whole-array assignment',(value,),dtype)
        value=self.coerce(value,dtype)
        if target["kind"]=="variable":
            if target.get('type',{}).get('flags',0)&1:
                return self.unsupported('assignment to const GLSL value',(value,),value.dtype)
            if target.get('global') and target.get('type',{}).get('flags',0)&4:
                return self.unsupported('assignment to read-only GLSL uniform',(value,),value.dtype)
            self.environment[target["name"]]=value
            if target.get('global'):self.globals[target['name']]=value
            return value
        if target['kind']=='member':
            prior=self.expression(target['object'],defer_read=True)
            indices=self.member_indices(prior.dtype,target['field'])
            if indices is None:return self.unsupported('unsupported shader member assignment',(value,))
            if len(set(indices))!=len(indices):return self.unsupported('duplicate shader swizzle assignment',(value,))
            components=list(self.parts(prior));assigned=self.parts(value)
            for index,part in zip(indices,assigned):components[index]=self.coerce(part,self.shape(prior.dtype)[0])
            updated=Field('components',tuple(components),prior.dtype)
            self.write(target['object'],updated)
            return value
        if target['kind']=='index':
            parent_type=target['object'].get('type',{})
            if parent_type.get('array'):
                if self.has_assignment(target['index']):return self.unsupported('shader index side-effect order unresolved',(value,))
                prior=self.expression(target['object'],defer_read=True);layout=self.array_type(prior.dtype)
                if layout is None:return self.unsupported('array write storage unresolved',(value,))
                element,length=layout;index=self.coerce(self.expression(target['index']),'int')
                self.effects.append(Field('index_guard',(index,),'bool',{'length':length}))
                updated=Field('array_write',(prior,index,self.coerce(value,element)),prior.dtype)
                self.write(target['object'],updated);return value
            if 'x' in parent_type.get('name',''):return self.unsupported('matrix row assignment is not a writable pinned-generator expression',(value,))
            if self.has_assignment(target['index']):return self.unsupported('shader index side-effect order unresolved',(value,))
            prior=self.expression(target['object'],defer_read=True);shape=self.shape(prior.dtype)
            if shape is None or shape[1]<2:return self.unsupported('unsupported indexed shader assignment',(value,))
            index=self.coerce(self.expression(target['index']),'int')
            self.effects.append(Field('index_guard',(index,),'bool',{'length':shape[1]}))
            components=[]
            for i,part in enumerate(self.parts(prior)):
                condition=Field('equal',(index,Field('constant',dtype='int',detail={'value':i})),'bool')
                components.append(Field('select',(condition,self.coerce(value,shape[0]),part),shape[0]))
            self.write(target['object'],Field('components',tuple(components),prior.dtype))
            return value
        return self.unsupported("indexed or indirect shader assignment",(value,))

    def expression(self,node:dict|None,*,defer_read=False)->Field:
        if node is None:return self.unsupported("uninitialized shader value")
        kind=node["kind"];dtype=node.get("type",{}).get("name","float")
        if node.get('type',{}).get('array'):
            environment=self.globals if node.get('global') else self.environment
            dtype=self.dtype(node['type'],actual=environment.get(node.get('name','')))
        if kind=="constant":
            value=node['value'];literal=node.get('renderer_literal')
            if literal is not None:
                try:value=float(literal.removeprefix('float(').removesuffix(')'))
                except ValueError:return self.unsupported('nonfinite or unsupported renderer literal',dtype=dtype)
            return Field("constant",dtype=dtype,detail={"value":value,'native_value':node['value'],'renderer_literal':literal})
        if kind=="variable":
            environment=self.globals if node.get('global') else self.environment
            value=environment.get(node["name"],Field("input",dtype=dtype,detail={"name":node["name"]}))
            return value if defer_read else self.read(value)
        if kind=="member":
            value=self.expression(node['object'],defer_read=True)
            if value.op in {'uninitialized','components','select'} or 'x' in value.dtype or self.shape(value.dtype)==(value.dtype,1):
                indices=self.member_indices(value.dtype,node['field'])
                if indices is None:return self.unsupported('unsupported shader member',dtype=dtype)
                components=self.parts(value);chosen=tuple(components[i] for i in indices)
                result=self.coerce(chosen[0],dtype) if len(chosen)==1 else Field('components',chosen,dtype)
            else:result=Field('member',(value,),dtype,{'field':node['field'],'swizzle':node.get('swizzle',False)})
            return result if defer_read else self.read(result)
        if kind=="index":
            if self.has_assignment(node['index']):
                return self.unsupported('array index side-effect order unresolved' if node['object'].get('type',{}).get('array')
                                        else 'shader index side-effect order unresolved',dtype=dtype)
            value=self.expression(node['object'],defer_read=True)
            op='array_index' if self.array_type(value.dtype) else 'index'
            result=Field(op,(value,self.coerce(self.expression(node['index']),'int')),dtype)
            return result if defer_read else self.read(result)
        if kind in {"construct","aggregate"}:
            args=tuple(self.expression(arg) for arg in node.get("args",node.get("elements",[])))
            matrix=re.fullmatch(r'(?:float|int|bool)([1-4])x([1-4])',dtype)
            if matrix:
                return self.matrix_constructor(args,dtype)
            return Field(kind,args,dtype)
        if kind=="cast":
            value=self.expression(node['operand'],defer_read=True)
            source=self.shape(value.dtype);target=self.shape(dtype)
            if source and target and 'x' not in value.dtype and 'x' not in dtype and value.op in {'uninitialized','components','select','loop_slot','loop_result'}:
                parts=self.parts(value)
                if source[1]==1:parts=parts*target[1]
                elif source[1]<target[1]:parts=parts+(Field('constant',dtype=target[0],detail={'value':0}),)*(target[1]-source[1])
                parts=tuple(self.coerce(part,target[0]) for part in parts[:target[1]])
                result=parts[0] if target[1]==1 else Field('components',parts,dtype)
            else:result=self.coerce(value,dtype)
            return result if defer_read else self.read(result)
        if kind=="unary":
            if node['operator'] in {3,4,5,6}:
                previous=self.expression(node['operand'])
                one=Field('constant',dtype=dtype,detail={'value':1})
                updated=Field('add' if node['operator'] in {3,5} else 'subtract',(self.coerce(previous,dtype),one),dtype)
                stored=self.write(node['operand'],updated)
                return stored if node['operator'] in {3,4} else previous
            if node['operator'] not in {0,1,2}:return self.unsupported('bitwise unary operator not lowered',dtype=dtype)
            return Field("unary",(self.expression(node["operand"]),),dtype,{"operator":node["operator"]})
        if kind=="conditional":
            if self.has_assignment(node):return self.unsupported('conditional expression side effects not lowered',dtype=dtype)
            return Field("select",tuple(self.expression(node[key]) for key in ["condition","yes","no"]),dtype)
        if kind=="binary":
            op=node["operator"]
            if 2<=op<16 and self.has_assignment(node):
                return self.unsupported('arithmetic/comparison side-effect order not established',dtype=dtype)
            matrix_product=op in {4,19} and 'x' in dtype
            if matrix_product and (not re.fullmatch(r'float([2-4])x\1',dtype)):
                return self.unsupported('rectangular bare matrix product has no pinned GLSL helper',dtype=dtype)
            if op in {0,1} and self.has_assignment(node):return self.unsupported('logical expression side effects not lowered',dtype=dtype)
            if op>=16:
                value=self.coerce(self.expression(node["right"]),dtype)
                if op!=16:value=Field('matrix_product' if matrix_product else {17:"add",18:"subtract",19:"multiply",20:"divide"}[op],(self.coerce(self.expression(node["left"]),dtype),value),dtype,
                                      {'zero_guard':True} if op==19 and not matrix_product else {})
                return self.write(node["left"],value)
            args=(self.expression(node['left']),self.expression(node['right']))
            if op in {2,3,4,5,6}:args=tuple(self.coerce(arg,dtype) for arg in args)
            elif op in {7,8,9,10,11,12,13,14,15}:
                names=[node[key]['type']['name'] for key in ['left','right']]
                if all(name in {'float','uint','int','bool'} for name in names):
                    common=next(name for name in ['float','uint','int','bool'] if name in names)
                    args=tuple(self.coerce(arg,common) for arg in args)
                elif op in {7,8,9,10,11,12}:
                    if names[0] in {'float','uint','int','bool'}:args=(self.coerce(args[0],names[1]),args[1])
                    elif names[1] in {'float','uint','int','bool'}:args=(args[0],self.coerce(args[1],names[0]))
            return Field('matrix_product' if matrix_product else BINARY[op],args,dtype,
                         {'zero_guard':True} if op==4 and not matrix_product else {})
        if kind=="call":
            name=node["function"];arguments=node.get("args",[])
            if name.lower().startswith("tex") and arguments:
                if name not in {'tex2D','tex3D','texCUBE'} or len(arguments)!=2:
                    return self.unsupported('texture sampling overload not lowered: '+name,dtype=dtype)
                sampler=self.expression(arguments[0])
                if sampler.op!='input':return self.unsupported("dynamic sampler expression",(sampler,),dtype)
                coordinates=self.expression(arguments[1])
                signature=node.get('signature',[])
                if len(signature)>1:coordinates=self.coerce(coordinates,signature[1]['type']['name'])
                result=self.texture(sampler.detail['name'],(coordinates,),dtype)
                return Field(result.op,result.args,result.dtype,{**result.detail,'intrinsic':name})
            args=tuple(self.expression(arg) for arg in arguments)
            signature=node.get('signature',[])
            args=tuple(self.coerce(arg,self.dtype(signature[i]['type'],actual=arg)) if i<len(signature) else arg
                       for i,arg in enumerate(args))
            if name in self.functions:return self.helper(node,args,dtype)
            if name not in PURE:return self.unsupported("shader helper/intrinsic not lowered: "+name,args,dtype)
            # Pinned GLSLGenerator implements DX9 compatibility using abs for
            # these intrinsics. Preserve its literal pow(x,1) sign exception.
            if name=='pow' and arguments[1]['kind']=='constant' and arguments[1]['value']==1:
                return self.coerce(args[0],dtype)
            if name in {'sqrt','rsqrt','log','log2','log10','pow'}:
                args=(Field('abs',(args[0],),args[0].dtype,
                            {'lowering':'pinned projectM DX9 compatibility'}),)+args[1:]
            result=Field(name,args,dtype)
            if name in {"sqrt","rsqrt","log","log2","log10","pow","normalize"}:
                return Field("domain_checked",(result,),dtype,{"function":name,"domain":"post-projectM-lowering domain requires proof"})
            return result
        return self.unsupported("shader expression not lowered: "+kind,dtype=dtype)

    def loop(self,statement):
        if self.has_assignment(statement.get('condition')):
            self.unsupported('loop condition side effects not lowered');return
        before=dict(self.environment)
        declared={d['name'] for s in statement.get('initialization',[]) if s['kind']=='declarations' for d in s['values']}
        self.statements(statement.get('initialization',[]))
        if statement.get('initial_expression') is not None:self.expression(statement['initial_expression'])
        initial=dict(self.environment);globals_initial=dict(self.globals)
        writes=set();global_writes=set()
        def targets(node):
            if isinstance(node,list):
                for item in node:targets(item)
            elif isinstance(node,dict):
                target=None
                if node.get('kind')=='binary' and node['operator']>=16:target=node['left']
                elif node.get('kind')=='unary' and node['operator'] in {3,4,5,6}:target=node['operand']
                if target is not None:
                    while target.get('kind') in {'member','index'}:target=target['object']
                    if target.get('kind')=='variable':
                        writes.add(target['name'])
                        if target.get('global'):global_writes.add(target['name'])
                for value in node.values():targets(value)
        targets(statement['body']);targets(statement.get('increment'))
        for name in global_writes:
            if name in initial and name in globals_initial and initial[name] is not globals_initial[name]:
                self.unsupported('loop global/local shadow alias unresolved');return
        names=tuple(sorted(writes & initial.keys()))
        global_aliases={name for name in names if name in globals_initial and initial[name] is globals_initial[name]}
        plan=LoopPlan(names)
        slots={name:Field('loop_slot',dtype=initial[name].dtype,detail={'plan':plan,'name':name}) for name in names}
        self.environment.update(slots)
        for name in names:
            if name in global_aliases:self.globals[name]=slots[name]
        plan.condition=self.expression(statement['condition']) if statement.get('condition') is not None else None
        outer_effects=self.effects;self.effects=[]
        self.scoped(statement['body'])
        if statement.get('increment') is not None:self.expression(statement['increment'])
        plan.effects=tuple(self.effects);self.effects=outer_effects
        plan.updates={name:self.environment[name] for name in names if self.environment[name] is not slots[name]}
        self.environment=initial;self.globals=globals_initial
        arguments=tuple(initial[name] for name in names)
        self.effects.append(Field('loop_result',arguments,'bool',{'plan':plan,'name':None}))
        for name in plan.updates:
            result=Field('loop_result',arguments,initial[name].dtype,{'plan':plan,'name':name,
                        'termination':'runtime checked; iteration budget is not a termination proof'})
            self.environment[name]=result
            if name in global_aliases:self.globals[name]=result
        for name in declared:
            if name in before:self.environment[name]=before[name]
            else:self.environment.pop(name,None)

    def statements(self,statements:list[dict]):
        for statement in statements:
            kind=statement["kind"]
            if kind=="expression":self.expression(statement["value"])
            elif kind=="declarations":
                for declaration in statement["values"]:
                    dtype=declaration['type']['name']
                    if declaration['type'].get('array'):value=self.array_declaration(declaration)
                    elif declaration['name'] in self._referenced_names(declaration['value']):
                        value=self.unsupported('same-name initializer binding differs in emitted GLSL',dtype=dtype)
                    else:value=self.initializer(self.expression(declaration['value']),dtype) if declaration['value'] is not None else Field('uninitialized',dtype=dtype,detail={'name':declaration['name']})
                    self.environment[declaration["name"]]=value
            elif kind=="block":self.scoped(statement["body"])
            elif kind in {'for','while'}:self.loop(statement)
            elif kind=="if":
                condition=self.expression(statement["condition"]);before=dict(self.environment);globals_before=dict(self.globals)
                outer_effects=self.effects;self.effects=[]
                self.scoped(statement["yes"]);yes=dict(self.environment);globals_yes=dict(self.globals)
                yes_effects=self.effects;self.effects=[]
                self.environment=dict(before);self.globals=dict(globals_before)
                self.scoped(statement["no"]);no=dict(self.environment);globals_no=dict(self.globals)
                no_effects=self.effects;self.effects=outer_effects
                true=Field('constant',dtype='bool',detail={'value':True})
                self.effects.extend(Field('select',(condition,effect,true),'bool') for effect in yes_effects)
                self.effects.extend(Field('select',(condition,true,effect),'bool') for effect in no_effects)
                self.globals={name:(globals_yes[name] if globals_yes[name]==globals_no[name]
                                   else Field('select',(condition,globals_yes[name],globals_no[name]),globals_yes[name].dtype))
                              for name in globals_before}
                for name in yes.keys()|no.keys():
                    y=yes.get(name,before.get(name));n=no.get(name,before.get(name))
                    if y is None or n is None:self.environment[name]=self.unsupported("branch-local lifetime not resolved")
                    elif y==n:self.environment[name]=y
                    else:self.environment[name]=Field("select",(condition,y,n),y.dtype)
            else:self.unsupported("shader statement not lowered: "+kind)

    @staticmethod
    def _referenced_names(node):
        if isinstance(node,list):return set().union(*(ShaderFields._referenced_names(n) for n in node))
        if not isinstance(node,dict):return set()
        result={node['name']} if node.get('kind')=='variable' else set()
        for value in node.values():result|=ShaderFields._referenced_names(value)
        return result
