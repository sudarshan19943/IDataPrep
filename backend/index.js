function parseBytes(file,headerFlag, socket){
    var reader = new FileReader();
    var flag = headerFlag;

    reader.onload= function(datafile) 
    {
      var  file =  datafile.target.result;
      console.log(file);
      socket.emit('loaddata',file,flag);
    };
    
    reader.readAsText(file);
}

