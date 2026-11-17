const fs=require('fs');
// Read the clean alipay.js from git on CN
const {execSync}=require('child_process');
try{
  // Try to get clean version from remote git
  execSync('git fetch origin main', {cwd:'/www/wwwroot/tools-cn.highkingflower.com', stdio:'pipe'});
  execSync('git checkout origin/main -- api/alipay.js', {cwd:'/www/wwwroot/tools-cn.highkingflower.com', stdio:'pipe'});
  console.log('Restored from git remote');
}catch(e){
  console.log('Git restore failed:', e.message.slice(0,80));
  // Fall back: read from the already-working C7 module and create minimal proxy
  console.log('Will create proxy modules instead');
}
// Check current state
const src=fs.readFileSync('/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js','utf8');
const firstLine=src.split('\n')[0];
console.log('First line length:', firstLine.length, 'bytes');
console.log('First char code:', firstLine.charCodeAt(0));
// Count total lines
console.log('Total lines:', src.split('\n').length);
// Check for C7 route
console.log('Has overfitcheck route:', src.includes("route.startsWith('/api/overfitcheck')"));
console.log('Has scan_api route:', src.includes("route.startsWith('/api/scan_api')"));
