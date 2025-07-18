module.exports = function ({ types: t }) {
  let tempVarCounter = 0;

  function getTempVar() {
    return t.identifier("tmp" + tempVarCounter++);
  }

  return {
    visitor: {
      Program: {
        enter(path) {
          tempVarCounter = 0;
        }
      },

      ReturnStatement(path) {
        const arg = path.node.argument;
        if (arg && !t.isIdentifier(arg) && !t.isLiteral(arg)) {
          const tmp = getTempVar();
          const decl = t.variableDeclaration("var", [
            t.variableDeclarator(tmp, arg),
          ]);
          path.insertBefore(decl);
          path.node.argument = tmp;
        }
      },

      ExpressionStatement(path) {
        const expr = path.node.expression;

        // func1(a + b)
        if (t.isCallExpression(expr)) {
          expr.arguments.forEach((arg, i) => {
            if (!t.isIdentifier(arg) && !t.isLiteral(arg)) {
              const tmp = getTempVar();
              const decl = t.variableDeclaration("var", [
                t.variableDeclarator(tmp, arg),
              ]);
              path.insertBefore(decl);
              expr.arguments[i] = tmp;
            }
          });
        }

        // x = y = 5 + 6;
        if (t.isAssignmentExpression(expr)) {
          const rhs = expr.right;
          if (!t.isIdentifier(rhs) && !t.isLiteral(rhs)) {
            const tmp = getTempVar();
            const decl = t.variableDeclaration("var", [
              t.variableDeclarator(tmp, rhs),
            ]);
            path.insertBefore(decl);
            expr.right = tmp;
          }
        }

        // 处理链式调用：var1.func1().func2().func3();
        if (t.isCallExpression(expr)) {
          const callChain = [];

          // 向内收集所有嵌套的 call
          let current = expr;
          while (
            t.isCallExpression(current) &&
            t.isMemberExpression(current.callee)
          ) {
            callChain.unshift(current); // 从内到外依次放入
            current = current.callee.object;
          }

          if (callChain.length > 1) {
            let prev = current; // 初始是最底层对象，例如 var1
            for (let i = 0; i < callChain.length; i++) {
              const origCall = callChain[i];
              const newCallee = t.memberExpression(prev, origCall.callee.property, origCall.callee.computed);
              const newCall = t.callExpression(newCallee, origCall.arguments);
              const tmp = getTempVar();
              const decl = t.variableDeclaration("var", [
                t.variableDeclarator(tmp, newCall)
              ]);
              path.insertBefore(decl);
              prev = tmp; // 下一层的对象
            }
            path.remove(); // 移除原始链式调用语句
          }
        }

      },
    },
  };
};
