from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent;E=ROOT/'docs/superpowers/evidence/current-patch-proof'
receipts=[]
sha=lambda b:hashlib.sha256(b).hexdigest()

def make(number,frame,crop,gain,folder=None,role_before='without-0',role_after='patched-0',name=None):
 folder=folder or W/'original-extra-captures'/(number+'-original')
 a=Image.open(folder/role_before/f'frame-{frame}.png').convert('RGB');b=Image.open(folder/role_after/f'frame-{frame}.png').convert('RGB')
 delta=ImageChops.difference(a,b);channels=delta.split();maximum=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]);heat=maximum.point(lambda v:min(255,v*gain)).convert('RGB');raw=delta.tobytes();changed=sum(any(raw[i:i+3]) for i in range(0,len(raw),3))
 image=Image.new('RGB',(1536,720),'#171717');d=ImageDraw.Draw(image);font=ImageFont.load_default(size=16)
 columns=[a,b,heat];labels=[f'Current WITHOUT {number}',f'Current WITH {number}',f'Absolute RGB difference x{gain}; clip255']
 w,h=a.size;display_scale=1 if w==512 else 2
 for col,(source,label) in enumerate(zip(columns,labels)):
  d.text((col*512+8,8),label,fill='white',font=font);shown=source if display_scale==1 else source.resize((512,288),Image.Resampling.NEAREST)
  image.paste(shown,(col*512,32))
  # Mark the same source rectangle in each whole-frame view.
  box=tuple(v*display_scale for v in crop);d.rectangle((col*512+box[0],32+box[1],col*512+box[2]-1,32+box[3]-1),outline='#ffffff',width=1)
  tile=source.crop(crop);zoom=min(480//tile.width,320//tile.height);tile=tile.resize((tile.width*zoom,tile.height*zoom),Image.Resampling.NEAREST)
  d.text((col*512+8,344),f'Aligned source crop {crop}, nearest {zoom}x',fill='white',font=font);image.paste(tile,(col*512+(512-tile.width)//2,376))
 d.text((8,704),f'Frame {frame}; changed {changed}/{w*h} pixels; mean absolute RGB delta {sum(raw)/len(raw):.6f}; max channel delta {max(raw)} /255. Raw images: no brightness gain.',fill='white',font=font)
 target=(name or number+'-visible')+'.png';image.save(E/target)
 record={'patch':number,'frame':frame,'dimensions':[w,h],'source_before':str(folder/role_before/f'frame-{frame}.png'),'source_after':str(folder/role_after/f'frame-{frame}.png'),'source_rgb_sha256':[sha(a.tobytes()),sha(b.tobytes())],'crop':list(crop),'whole_frame_nearest_scale':display_scale,'difference_map':'max(abs(before.RGB-after.RGB))','map_gain':gain,'map_clip':255,'raw_brightness_changed':False,'whole_frame_crop_outline':True,'changed_pixels':changed,'total_pixels':w*h,'mean_absolute_rgb8_delta':sum(raw)/len(raw),'maximum_channel_delta':max(raw),'image':target,'image_sha256':sha((E/target).read_bytes())}
 receipts.append(record)
 return record
# Select the earlier retained frame for texture feedback, rather than the quieter endpoint.
a=Image.open(W/'original-extra-captures/0009-original/without-0/frame-29.png').convert('RGB');b=Image.open(W/'original-extra-captures/0009-original/patched-0/frame-29.png').convert('RGB');diff=ImageChops.difference(a,b);raw=diff.tobytes();offset=max(range(len(raw)),key=raw.__getitem__);x=(offset//3)%512;y=(offset//3)//512;left=max(0,min(512-96,x-48));top=max(0,min(288-64,y-32));make('0009',29,(left,top,left+96,top+64),8)
make('0012',29,(120,64,144,80),4)
make('0013',29,(120,64,144,80),4)
make('0007',119,(170,60,322,212),1,W/'fixture-captures/0007-wave-mode',name='0007-wave-mode-visible')
make('0007',29,(160,52,320,212),2,W/'wave-witness-captures/0007-wormhole',name='0007-wormhole-visible')
(E/'visibility-figures.json').write_text(json.dumps(receipts,indent=2)+'\n')
for r in receipts:print(r['patch'],r['frame'],r['changed_pixels'],r['maximum_channel_delta'],r['image'])
