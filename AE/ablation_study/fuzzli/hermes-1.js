var NISLFuzzingFunc = 
function(a) {
    switch (a = 0, arguments[0]) {
      case 0:
        return "PASS";

      case 1:
        return "FAIL";
    }
}
;
var NISLParameter0 = -67;
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);
print(NISLCallingResult);