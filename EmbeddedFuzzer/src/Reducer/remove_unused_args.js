const fs = require('fs');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');

const filename = process.argv[2];
if (!filename) {
  console.error("Usage: node optimize_unused_args.js <filename.js>");
  process.exit(1);
}

const code = fs.readFileSync(filename, 'utf8');
const ast = parser.parse(code, {
  sourceType: 'module',
});

// 保存未使用参数名
const unusedParams = new Set();
// 记录形参与其所在函数的绑定关系
let targetFunctionId = null;
let targetFunctionParams = [];
let usedIdentifiers = new Set();

// 第一步：定位目标函数 NISLa
traverse(ast, {
  VariableDeclarator(path) {
    if (
      t.isIdentifier(path.node.id, { name: 'NISLa' }) &&
      (t.isFunctionExpression(path.node.init) || t.isArrowFunctionExpression(path.node.init))
    ) {
      targetFunctionId = path.node.id.name;
      targetFunctionParams = path.node.init.params.map(p => p.name);

      // 查找函数体中使用了哪些参数
      path.traverse({
        Identifier(innerPath) {
          if (
            targetFunctionParams.includes(innerPath.node.name) &&
            !t.isFunction(innerPath.parent) && // 不要算在其他嵌套函数中定义的
            !t.isFunctionDeclaration(innerPath.parent)
          ) {
            usedIdentifiers.add(innerPath.node.name);
          }
        },
      });

      for (const p of targetFunctionParams) {
        if (!usedIdentifiers.has(p)) {
          unusedParams.add(p);
        }
      }

      // 删除未使用形参
      path.node.init.params = path.node.init.params.filter(p => !unusedParams.has(p.name));
    }
  },
});

// 第二步：删除调用实参和变量定义
const removeVarDeclarators = new Set();
traverse(ast, {
  CallExpression(path) {
    if (t.isIdentifier(path.node.callee, { name: targetFunctionId })) {
      const newArgs = [];
      path.node.arguments.forEach((arg, index) => {
        const param = targetFunctionParams[index];
        if (!unusedParams.has(param)) {
          newArgs.push(arg);
        } else if (t.isIdentifier(arg)) {
          removeVarDeclarators.add(arg.name);
        }
      });
      path.node.arguments = newArgs;
    }
  },
});
// console.log(removeVarDeclarators);
traverse(ast, {
  VariableDeclarator(path) {
    if (removeVarDeclarators.has(path.node.id.name)) {
      path.remove();
    }
  }
});

// 输出优化后的代码
const output = generate(ast, { retainLines: true }).code;
console.log(output);
