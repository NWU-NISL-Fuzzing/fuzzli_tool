var NISLFuzzingFunc = 
function() {
    var arr = [];
    arr[Math.pow(2, 32) - 2] = true;
    return arr.indexOf(true, Infinity) === -1;
}
;
var NISLCallingResult = NISLFuzzingFunc();
print(NISLCallingResult);