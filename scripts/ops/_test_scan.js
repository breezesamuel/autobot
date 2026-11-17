const http=require('http');
const opts={hostname:'127.0.0.1',port:8794,path:'/api/scan_api?action=rate&ref=test_xxx',method:'GET'};
const req=http.request(opts,function(res){
  let data='';
  res.on('data',c=>data+=c);
  res.on('end',()=>{
    console.log('HTTP '+res.statusCode);
    try{console.log(JSON.stringify(JSON.parse(data),null,2));}
    catch(e){console.log('RAW:',data.slice(0,300));}
  });
});
req.on('error',e=>console.log('REQ ERR:',e.message));
req.end();
