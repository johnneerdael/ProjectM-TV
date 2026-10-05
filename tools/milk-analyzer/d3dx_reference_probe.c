/* Optional Windows CPU-only reflection probe. No D3D device, rendering or app control.
 * Dynamically loads caller-supplied D3DX DLL; never links or distributes Microsoft binaries.
 * Usage: probe.exe shader.hlsl profile DLL-path [flags]. */
#define COBJMACROS
#include <windows.h>
#include <d3dx9shader.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef HRESULT (WINAPI *compile_fn)(LPCSTR,UINT,const D3DXMACRO*,LPD3DXINCLUDE,LPCSTR,LPCSTR,DWORD,LPD3DXBUFFER*,LPD3DXBUFFER*,LPD3DXCONSTANTTABLE*);
typedef HRESULT (WINAPI *disassemble_fn)(const DWORD*,BOOL,LPCSTR,LPD3DXBUFFER*);
int main(int argc,char** argv){
 if(argc!=4 && argc!=5)return 2;
 DWORD flags=argc==5?(DWORD)strtoul(argv[4],NULL,10):1u<<16;
 HMODULE lib=LoadLibraryA(argv[3]);if(!lib){fprintf(stderr,"LoadLibrary error=%lu\n",GetLastError());return 3;}
 char module[MAX_PATH];GetModuleFileNameA(lib,module,MAX_PATH);printf("MODULE %s\n",module);
 compile_fn compile=(compile_fn)GetProcAddress(lib,"D3DXCompileShader");
 disassemble_fn disassemble=(disassemble_fn)GetProcAddress(lib,"D3DXDisassembleShader");
 if(!compile||!disassemble)return 4;
 FILE* f=fopen(argv[1],"rb");if(!f)return 5;fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);
 char* source=calloc(n+1,1);if(fread(source,1,n,f)!=(size_t)n)return 6;fclose(f);
 LPD3DXBUFFER code=NULL,errors=NULL,assembly=NULL;LPD3DXCONSTANTTABLE table=NULL;
 HRESULT hr=compile(source,(UINT)n,NULL,NULL,"PS",argv[2],flags,&code,&errors,&table);
 printf("HRESULT %08lx FLAGS %lu PROFILE %s\n",(unsigned long)hr,(unsigned long)flags,argv[2]);
 if(errors)printf("DIAGNOSTICS\n%s\n",(const char*)errors->lpVtbl->GetBufferPointer(errors));
 if(FAILED(hr))return 7;
 D3DXCONSTANTTABLE_DESC td;table->lpVtbl->GetDesc(table,&td);printf("CONSTANTS %u\n",td.Constants);
 for(UINT i=0;i<td.Constants;i++){
  D3DXHANDLE h=table->lpVtbl->GetConstant(table,NULL,i);D3DXCONSTANT_DESC d;UINT count=1;
  if(FAILED(table->lpVtbl->GetConstantDesc(table,h,&d,&count)))return 8;
  printf("CONSTANT name=%s set=%u register=%u count=%u class=%u type=%u rows=%u columns=%u bytes=%u default=",d.Name,d.RegisterSet,d.RegisterIndex,d.RegisterCount,d.Class,d.Type,d.Rows,d.Columns,d.Bytes);
  if(d.DefaultValue){const float* values=(const float*)d.DefaultValue;for(UINT j=0;j<d.Bytes/4;j++)printf("%s%.9g",j?",":"",values[j]);}else printf("NULL");puts("");
 }
 if(SUCCEEDED(disassemble((const DWORD*)code->lpVtbl->GetBufferPointer(code),FALSE,NULL,&assembly)))printf("ASSEMBLY\n%s\n",(const char*)assembly->lpVtbl->GetBufferPointer(assembly));
 return 0;
}
