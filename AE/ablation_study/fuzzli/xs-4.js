var NISLFuzzingFunc = function (modified, path) {
    if (modified[path]) {
    }
    var sp = path.split('.');
    var cur = sp[0];
    for (var INDEX = 0; INDEX < 1000; INDEX++) {
        for (var i = 0; i < sp.length; ++i) {
            if (modified[cur]) {
            }
            cur += '.' + sp[i];
        }
    }
    return false;
};
var NISLParameter0 = [undefined];
var NISLParameter1 = 'AQFe&KJoQe{h}`>J^c|^v<HpMs9bv-ZvF~F].`0@qp4B#$lcjL%KYgqGB[:|#5GV)4%WdhI<>}mULh{2NHu;gJQ4nHsf=<brLz~gzh.';
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0, NISLParameter1);
print(NISLCallingResult);