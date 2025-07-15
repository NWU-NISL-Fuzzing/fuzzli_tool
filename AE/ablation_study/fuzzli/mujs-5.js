var NISLFuzzingFunc = 
function() {
    var schema = {
        type: "integer"
    };
    for (NISLi = 0; NISLi < 16 - 1; NISLi++) {
        schema['prop-' + NISLi] = 1;
    }
    schema['foo'] = 123;
    for (NISLi = 0; NISLi < 1e4; NISLi++) {
        var odp = Object.defineProperties(schema,schema);
    }
    //object method mutation
    if (this.hasMinValue) {
        schema.minimum = this.opts.min;
    }
    if (this.hasMaxValue) {
        schema.maximum = this.opts.max;
    }
    if (this.description) {
        schema.description = this.description;
    }
    return schema;
}
;
var NISLCallingResult = NISLFuzzingFunc();
print(NISLCallingResult);