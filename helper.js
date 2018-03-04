function hideAll() {
	console.log('hideAll');
}

function showme(clicked) {
	console.log('showme');
	var idVal = clicked.substring(7);
	var all = document.getElementsByName("data");
	var i;
	for (i = 0; i < all.length; i++) {
		all[i].style.display = "none";
	}
	var allSum = document.getElementsByName("summary");
        for (i = 0; i < allSum.length; i++) {
                allSum[i].style.display = "none";
        }
          var all = document.getElementsByName("accordian");
	var i;
	for (i = 0; i < all.length; i++) {
		all[i].style.display = "none";
	}
        
        if (document.getElementById('option2').checked) {
  rate_value = document.getElementById('option2').value;
  idVal = idVal+"-"+rate_value
  } 
 
	document.getElementById(idVal).style.display = "block";

}
