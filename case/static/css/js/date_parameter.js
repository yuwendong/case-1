var all_startDate = new Date('09/01/2013');
var all_endDate = new Date('09/21/2013');
var all_maxDate = new Date('09/21/2013');
var all_minDate = new Date('09/01/2013');
var week_ago = subtract(all_endDate,7);
//var month_ago = subtract(all_endDate,30);
//var 3month_ago = subtract(all_endDate,90);

function subtract(date,days){
var nd = new Date(date);
   nd = nd.valueOf();
   nd = nd - days * 24 * 60 * 60 * 1000;
   nd = new Date(nd);
var y = nd.getFullYear();
var m = nd.getMonth()+1;
var d = nd.getDate();
if(m <= 9) m = "0"+m;
if(d <= 9) d = "0"+d; 
var cdate = y+"-"+m+"-"+d;
return cdate;
}