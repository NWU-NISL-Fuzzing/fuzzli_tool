let {getValues} = require("../../../text_to_code/src/main/main");

apiInfo = []
apiInfo["name"] = "Array.prototype.push";
apiInfo["argsNumber"] = 2;
let boundaryCondition = getValues(apiInfo);
console.log(boundaryCondition);