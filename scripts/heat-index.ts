// NOAA heat-index equation, https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
function bounded(value:unknown,min:number,max:number){return typeof value==='number'&&Number.isFinite(value)&&value>=min&&value<=max?value:null;}
export function weatherHeatIndex(temperature:unknown,humidity:unknown):number|null {
  const c=bounded(temperature,-90,65),h=bounded(humidity,0,100);if(c===null||h===null)return null;
  const t=c*9/5+32,simple=.5*(t+61+(t-68)*1.2+h*.094);
  let index=(simple+t)/2;
  if(index>=80){
    index=-42.379+2.04901523*t+10.14333127*h-.22475541*t*h-.00683783*t*t-.05481717*h*h+.00122874*t*t*h+.00085282*t*h*h-.00000199*t*t*h*h;
    if(h<13&&t>=80&&t<=112)index-=((13-h)/4)*Math.sqrt((17-Math.abs(t-95))/17);
    else if(h>85&&t>=80&&t<=87)index+=((h-85)/10)*((87-t)/5);
  }
  return (index-32)*5/9;
}

export function heatBand(indexC:number):'green'|'amber'|'red' {
  const f=indexC*9/5+32;
  return f>=103?'red':f>=80?'amber':'green';
}
