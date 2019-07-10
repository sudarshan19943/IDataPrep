function parseBytes(file,jsonData,headersFlag,taskFlag,socket){
    var reader = new FileReader();


    reader.onload= function(datafile) 
    {
      var  file =  datafile.target.result;
      console.log(file);
      socket.emit('loaddata',file,jsonData,headersFlag,taskFlag);
    };
    
    reader.readAsText(file);
}

function parserJson(socket)
{

  socket.emit('feat');
}
