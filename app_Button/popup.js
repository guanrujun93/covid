let TargetData = '';
function summarize(TargetData) {

let Target = JSON.stringify(TargetData);
	chrome.tabs.executeScript({
	code: 'var config='+Target
	}, function() {
	    chrome.tabs.executeScript({file: 'background.js'})
		//alert("Run1");
	});
}
window.addEventListener('load', function load(event){
	var createButton = document.getElementById('AnalyzeMe');
	createButton.addEventListener('click', function() { summarize(''); });
})



