


var config;
if(config!=undefined){
	function Hilitor(tag){
		var targetNode = document.body;
		var hiliteTag = "MARK";
		var skipTags = new RegExp("^(?:" + hiliteTag + "|SCRIPT)$");
		var colors = ["#f57931"];
		var wordColor = [];
		var colorIdx = 0;
		var matchRegExp = "";
		var openLeft = false;
		var openRight = false;
		// characters to strip from start and end of the input string
		var endRegExp = new RegExp('^[^\\w]+|[^\\w]+$', "g");
		// characters used to break up the input string into words
		// var breakRegExp = new RegExp('[^\\w\'-]+', "g");
		var breakRegExp = endRegExp;

		this.setEndRegExp = function(regex) {
			endRegExp = regex;
			return endRegExp;
		};

		this.setBreakRegExp = function(regex) {
		    breakRegExp = regex;
		    return breakRegExp;
		};

		this.setMatchType = function(type){
		    switch(type){
		      case "left":
		        this.openLeft = false;
		        this.openRight = true;
		        break;
		      case "right":
		        this.openLeft = true;
		        this.openRight = false;
		        break;
		      case "open":
		        this.openLeft = this.openRight = true;
		        break;
		      default:
		        this.openLeft = this.openRight = false;
		    }
		};

		this.setRegex = function(input){
		    input = input.replace(endRegExp, "");
		    input = input.replace(breakRegExp, "|");
		    input = input.replace(/^\||\|$/g, "");
		    if(input) {
		    	var re = "(" + input + ")";
		    	if(!this.openLeft) {
		        re = "\\b" + re;
		    }
		    if(!this.openRight) {
		        re = re + "\\b";
		    }
		    matchRegExp = new RegExp(re, "i");
		    return matchRegExp;
		    }
		    return false;
		  };

		this.getRegex = function(){
		    var retval = matchRegExp.toString();
		    retval = retval.replace(/(^\/(\\b)?|\(|\)|(\\b)?\/i$)/g, "");
		    retval = retval.replace(/\|/g, " ");
			//alert(resp[key].sentence);
		    return retval;
		};

		// recursively apply word highlighting
		this.hiliteWords = function(node){
		    if(node === undefined || !node) return;
		    if(!matchRegExp) return;
		    if(skipTags.test(node.nodeName)) return;

		    if(node.hasChildNodes()) {
		      for(var i=0; i < node.childNodes.length; i++)
		        this.hiliteWords(node.childNodes[i]);
		    }
		    if(node.nodeType == 3) { // NODE_TEXT
		      if((nv = node.nodeValue) && (regs = matchRegExp.exec(nv))) {
				regs[0] = nv;
				//alert(nv);
		        if(!wordColor[regs[0].toLowerCase()]) {
		          wordColor[regs[0].toLowerCase()] = colors[colorIdx++ % colors.length];
		        }

		        var match = document.createElement(hiliteTag);
		        match.appendChild(document.createTextNode(regs[0]));
		        match.style.backgroundColor = wordColor[regs[0].toLowerCase()];
		        match.style.color = "#000";

		        var after = node.splitText(regs[0].index);
		        after.nodeValue = after.nodeValue.substring(regs[0].length);
		        node.parentNode.insertBefore(match, after);
		      }
		    };
	  	};

	  	// remove highlighting
	  	this.remove = function(){
		    var arr = document.getElementsByTagName(hiliteTag);
		    while(arr.length && (el = arr[0])) {
		    	var parent = el.parentNode;
		    	parent.replaceChild(el.firstChild, el);
		    	parent.normalize();
		    }
		};

	  	// start highlighting at target node
	  	this.apply = function(input){
		    // this.remove();
		    if(input === undefined || !(input = input.replace(/(^\s+|\s+$)/g, ""))) {
		      return;
		    }
		    if(this.setRegex(input)) {
		      this.hiliteWords(targetNode);
		    }
		    return matchRegExp;
		};
	}
	
	

		
	//excel
function PostUser(answers)
    {
	const API_URL = '/api'
	var req = new XMLHttpRequest();

  	var user = answers;	
	var settings1 = {
	"async": true,
	"crossDomain": true,
	"url": "http://127.0.0.1:5000/NewUserName",
	"method": "POST",
	"headers": {
	  "content-type": "application/json"
	},
	"test": JSON.stringify(user),
	}
  	var post_data = JSON.stringify({"test":encodeURIComponent(user)});
  	xhttp.open(settings1.method, settings1.url, settings1.async);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(post_data);	
	}//excel
	
	// function unicodeToChar(text) {
	// 	alert("Generating summary highlights. This may take up to 30 seconds depending on length of article.");
	// 	return text.replace(/\\u[\dA-F]{4}/gi,
	// 	function (match) {
	// 		return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
	//     });
	// }
	let TrainData = document.body.innerText;
	let TargetData = 'check';
	let source_url = window.location.href;
	var settings = {
	"async": true,
	"crossDomain": true,
	"url": "http://127.0.0.1:5000/analyze",
	"method": "POST",
	"headers": {
	  "content-type": "application/json"
	},
	"article": JSON.stringify(TrainData),
	"test_data": JSON.stringify(TargetData)

	}
	
	 var xhttp = new XMLHttpRequest();
 	 xhttp.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
	       	var myHilitor = new Hilitor();
	       	myHilitor.remove();
	       	var obj = JSON.parse(this.responseText);
			var model_result = obj.result;
			var model_user = obj.user;
			if ( model_user == 'new' )//New User//
			{
				Swal.mixin({				  
				  confirmButtonText: 'OK! &rarr;',
				  showCancelButton: true,
				  //progressSteps: ['1', '2', '3']
				}).queue([
				  {
					input: 'text',
					title: 'New User!',
					text: 'Register your name or ID first to view the results!',
					inputValidator: (value) => {
					if (!value) {
					  return 'You need to write your name or ID!'
					}
				  }
				  
				  },
				  'User Added!'
				]).then((result) => {
				  if (result.value) {
						const answers = JSON.stringify(result.value[0])
						PostUser(answers);
						var model_result = obj.result;
						if (model_result != 'NONE')
							{
							if (model_result == 'REAL'|| model_result == 'TRUE')
								{	
								Swal.fire('',"This page contains accurate information on COVID-19.",'success') }
							else
								{
								//Swal.fire('Alert!',"The highlighted sections on this page contain inaccurate information on COVID-19.",'warning')
								Swal.fire({
								  title: 'Alert!',
								  text: " The highlighted sections on this page contain inaccurate information on COVID-19.",
								  icon: 'warning',
								  showCancelButton: true,
								  confirmButtonColor: '#3085d6',
									cancelButtonColor: '#d33',
								  confirmButtonText: 'Show highlighted text!'
								}).then((result) => {
								  if (result.isConfirmed) {
								if(obj.match==true)
									{
									var resp = obj.resp;
									for (var key in resp)
										{
										myHilitor.apply(resp[key].sentence);
										}
									}
								  }
								})
								}
							}
						else{
							Swal.fire('',"The content on this web page is unrelated to COVID-19. We are unable to provide a result on the validity of the content.",'info')
							}					
				  }
				})		
			}//NewUser end
			
			if ( model_user == 'old' )//OldUser
			{
				var model_result = obj.result;
				if (model_result != 'NONE')
					{
					if (model_result == 'REAL'|| model_result == 'TRUE')
						{	
						Swal.fire('',"This page contains accurate information on COVID-19.",'success') }
					else
						{
							Swal.fire({
								  title: 'Alert!',
								  text: " The highlighted sections on this page contain inaccurate information on COVID-19.",
								  icon: 'warning',
								  showCancelButton: true,
								    confirmButtonColor: '#3085d6',
									cancelButtonColor: '#d33',
								  confirmButtonText: 'Show highlighted text!'
								}).then((result) => {
								  if (result.isConfirmed) {
								if(obj.match==true)
									{
									var resp = obj.resp;
									for (var key in resp)
										{
										myHilitor.apply(resp[key].sentence);
										}
									}
								  }
								})

						}
					}
				else{
					Swal.fire('',"The content on this web page is unrelated to COVID-19. We are unable to provide a result on the validity of the content.",'info')
					}
			}//OldUser
    	}
  	};



  
	
  	var post_data = JSON.stringify({"article":encodeURIComponent(TrainData),"test_data":encodeURIComponent(TargetData),"url":encodeURIComponent(source_url)});
  	xhttp.open(settings.method, settings.url, settings.async);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(post_data);
}

//}*/
