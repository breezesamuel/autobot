const fs=require('fs');
const path='/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
let src=fs.readFileSync(path,'utf8');
// Strip BOM/corrupt prefix
while(src.length>0 && (src.charCodeAt(0)<32||src.charCodeAt(0)===65533)){src=src.slice(1);}
// Remove any line containing literal \n after { (the corruption pattern)
const lines=src.split('\n');
const clean=[];
for(const l of lines){
  if(l.includes('\\n')&&l.includes('route.startsWith'))continue;
  clean.push(l);
}
src=clean.join('\n');
fs.writeFileSync(path,src,'utf8');
console.log('Cleaned, lines:',clean.length,'size:',fs.statSync(path).size);
try{require('child_process').execSync('node --check "'+path+'"',{stdio:'pipe'});console.log('SYNTAX OK');}
catch(e){console.log('STILL BROKEN:',e.message.slice(0,120));}
