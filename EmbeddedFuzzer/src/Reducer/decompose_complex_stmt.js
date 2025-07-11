module.exports = function ({ types: t }) {
  return {
    visitor: {
      ExpressionStatement(path) {
        console.log("ExpressionStatement");
        const expr = path.node.expression;
        if (
          (t.isCallExpression(expr) || t.isAssignmentExpression(expr)) &&
          !t.isIdentifier(expr)
        ) {
          const extracted = extractSubexpressions(t, expr);
          if (extracted) {
            path.replaceWithMultiple(extracted);
          }
        }
      },
      ReturnStatement(path) {
        console.log("ReturnStatement");
        if (path.node.argument && !t.isIdentifier(path.node.argument)) {
          const tmp = path.scope.generateUidIdentifier("tmp");
          const decl = t.variableDeclaration("var", [
            t.variableDeclarator(tmp, path.node.argument),
          ]);
          const ret = t.returnStatement(tmp);
          path.replaceWithMultiple([decl, ret]);
        }
      },
      IfStatement(path) {
        console.log("IfStatement");
        const test = path.node.test;
        if (!t.isIdentifier(test) && !t.isLiteral(test)) {
          const tmp = path.scope.generateUidIdentifier("tmp");
          const tmpDecl = t.variableDeclaration("var", [
            t.variableDeclarator(tmp, test),
          ]);
          path.node.test = tmp;
          path.insertBefore(tmpDecl);
        }
      }
    },
  };
};

function extractSubexpressions(t, expr) {
  const tmp = t.identifier("_tmp1");
  const decl = t.variableDeclaration("var", [
    t.variableDeclarator(tmp, expr),
  ]);
  return [decl];
}
