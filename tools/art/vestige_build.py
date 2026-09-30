import json,os
import numpy as np
from PIL import Image
from kit import idle_frames, appear_frames, vanish_frames
AUR={'V01':((255,120,40),(255,220,140)),'V02':((120,200,90),(210,255,170)),'V03':((70,200,210),(200,250,255)),'V04':((150,170,255),(230,235,255)),
'V05':((255,230,150),(255,255,230)),'V06':((110,200,180),(210,255,240)),'V07':((150,210,255),(240,250,255)),'V08':((150,80,220),(220,190,255))}
man=json.load(open('out/manifest.json'))
for m in man:
  base=np.array(Image.open(f'out/{m["id"]}/base.png'))
  au,mo=AUR[m['id']]
  idle=idle_frames(base,8,au,mo,seed=int(m['id'][1:]))
  ap=appear_frames(idle[0],8,edge=np.array((255,255,255),np.uint8),glow=np.array(mo,np.uint8))
  va=vanish_frames(idle[0],6,col=np.array(mo,np.uint8))
  d=f'out/{m["id"]}/frames'; os.makedirs(d,exist_ok=True)
  i=0; tags=[]
  for tag,fr in [('appear',ap),('idle',idle),('vanish',va)]:
    s=i
    for f in fr: Image.fromarray(f).save(f'{d}/{i:03d}.png'); i+=1
    tags.append([tag,s+1,i])
  m['frames']=i; m['tags']=tags; m['durations']=[70]*8+[120]*8+[80]*6; m['frame_size']=list(Image.open(f'{d}/000.png').size)
json.dump(man,open('out/manifest.json','w'),indent=1)
