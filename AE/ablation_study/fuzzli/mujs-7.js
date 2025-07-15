var NISLFuzzingFunc = 
function() {
    //regex method mutation
    return function(doc) {
        if (!doc) return;
        if (doc.type === "directive") {
            return doc.name.replace(/zyKZSaoXGU3heHJapiGTcuwdyIu^*/i, function($1) {
                return "-" + $1.toLowerCase();
            });
        }
        return doc.label || doc.name;
    };
}
;
var NISLCallingResult = NISLFuzzingFunc();
print(NISLCallingResult);