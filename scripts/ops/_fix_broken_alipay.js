const fs=require('fs');
const path='/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
// Read the current broken file to get its structure
let src;
try{
  src=fs.readFileSync(path,'utf8');
}catch(e){
  console.log('Cannot read:',e.message);process.exit(1);
}
// Check if it has BOM
if(src.charCodeAt(0)===0xFEFF||src.charCodeAt(0)===65533){
  console.log('File has BOM/corruption at start, will fix');
  // Remove any leading BOM/non-ASCII chars
  let clean='';
  let i=0;
  while(i<src.length && (src.charCodeAt(i)<32||src.charCodeAt(i)>126)){i++;}
  src=src.slice(i);
  console.log('Stripped',i,'corrupt bytes from start');
}
// Now find and remove the broken scan_api line(s)
// The broken content is around line 1749: if(route.startsWith('/api/scan_api')){{\n
const badPattern=/    if\(route\.startsWith\(\'\/api\/scan_api\'\)\)\{\{\n/m;
if(badPattern.test(src)){
  src=src.replace(badPattern,'    // C18 scan_api route was here\n');
  console.log('Removed broken scan_api block');
}else{
  console.log('No broken scan_api pattern found');
}
// Also check for other potentially corrupted blocks
const lines=src.split('\n');
let healthyLines=[];
let inBadBlock=false;
for(let i=0;i<lines.length;i++){
  const l=lines[i];
  // Skip lines that have literal \n in them (escaped newlines that broke syntax)
  if(l.includes('\\n') && l.includes('route.startsWith')){
    console.log('Skipping corrupted line '+i+': '+l.slice(0,60));
    inBadBlock=true;
    continue;
  }
  if(inBadBlock && l.trim()===''){
    continue; // skip blank line after corrupted block
  }
  if(inBadBlock && !l.includes('//') && l.trim().length>0){
    inBadBlock=false; // block ended
  }
  if(!inBadBlock){
    healthyLines.push(l);
  }
}
src=healthyLines.join('\n');
console.log('Cleaned: {} -> {} lines'.format(lines.length,healthyLines.length));
// Write back
fs.writeFileSync(path,src,'utf8');
console.log('Written back, size='+fs.statSync(path).size);
// Verify
const {execSync}=require('child_process');
try{
  execSync('node --check "'+path+'"',{stdio:'pipe'});
  console.log('SYNTAX OK after cleanup');
}catch(e){
  console.log('Still has syntax error:',e.message.slice(0,100));
}
