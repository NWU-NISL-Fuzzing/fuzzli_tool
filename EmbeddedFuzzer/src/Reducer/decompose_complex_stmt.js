// decompose_complex_stmt.js
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
      },
    },
  };
};
