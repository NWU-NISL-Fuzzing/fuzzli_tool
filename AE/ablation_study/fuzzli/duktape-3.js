for (var INDEX = 0; INDEX < 1000; INDEX++) {
    var NISLFuzzingFunc = function () {
        var a = 1;
        return a === ++a;
    };
}
var NISLCallingResult = NISLFuzzingFunc();
print(NISLCallingResult);