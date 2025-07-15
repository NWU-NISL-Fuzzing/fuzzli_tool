const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const fs = require("fs");

// 获取命令行参数
const filename = process.argv[2];
const targetIndices = process.argv[3].split(',').map(Number);

// 用于快速判断的集合
const indexSet = new Set(targetIndices);

// 从文件中读取代码并解析为 AST
const code = fs.readFileSync(filename, 'utf-8');
const ast = parser.parse(code, { sourceType: "script" });

const leafStatements = [];
const declaredVars = new Set();  // 收集用户定义的变量名

// 判断语句级叶子节点
function isLeafStatement(path) {
  if (!path.isStatement()) return false;
  if (path.isReturnStatement()) return false;

  let hasStatementChild = false;
  path.traverse({
    Statement(childPath) {
      if (childPath !== path) {
        hasStatementChild = true;
        childPath.stop();
      }
    }
  });

  return !hasStatementChild;
}

// 遍历收集声明的变量名（全局）
traverse(ast, {
  VariableDeclarator(path) {
    if (path.node.id.type === 'Identifier') {
      declaredVars.add(path.node.id.name);
    }
  },
  FunctionDeclaration(path) {
    if (path.node.id) {
      declaredVars.add(path.node.id.name);
    }
    path.node.params.forEach(param => {
      if (param.type === 'Identifier') {
        declaredVars.add(param.name);
      }
    });
  },
  ClassDeclaration(path) {
    if (path.node.id) {
      declaredVars.add(path.node.id.name);
    }
  },
  // 也考虑箭头函数的参数
  ArrowFunctionExpression(path) {
    path.node.params.forEach(param => {
      if (param.type === 'Identifier') {
        declaredVars.add(param.name);
      }
    });
  }
});

// 收集语句级别的叶子节点
traverse(ast, {
  enter(path) {
    if (isLeafStatement(path)) {
      leafStatements.push(path);
    }
  }
});

// 提取变量名：只保留在用户代码中声明的变量
const usedVars = new Set();

targetIndices.forEach(i => {
  const path = leafStatements[i];
  if (!path) return;

  path.traverse({
    Identifier(p) {
      const name = p.node.name;
      if (declaredVars.has(name)) {
        usedVars.add(name);
      }
    }
  });
});

console.log([...usedVars]);
