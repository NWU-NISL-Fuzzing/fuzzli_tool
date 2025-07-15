var NISLFuzzingFunc = 
function(options) {
    return this.global && !(options && options.toplevel) || this.undeclared || !(options && options.eval) && (this.scope.uses_eval || this.scope.uses_with);
}
;
var NISLParameter0 = true;
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);
print(NISLCallingResult);