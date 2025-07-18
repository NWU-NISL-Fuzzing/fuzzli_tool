const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generator = require("@babel/generator").default;
const t = require("@babel/types");

let code = '';
process.stdin.on('data', chunk => code += chunk);
process.stdin.on('end', () => {
    const ast = parser.parse(code, { sourceType: "script" });

    let counter = 0;
    const leafStatements = [];

    function isLeafStatement(path) {
        if (!path.isStatement()) return false;
        if (path.isReturnStatement()) return false;

        // Check if it has any children that are statements
        let hasStatementChild = false;
        path.traverse({
            Statement(childPath) {
                if (childPath !== path) {
                    hasStatementChild = true;
                    childPath.stop(); // early exit
                }
            }
        });

        return !hasStatementChild;
    }

    traverse(ast, {
        enter(path) {
            if (isLeafStatement(path)) {
                leafStatements.push({ path, label: `leaf_stmt_${counter}` });
                counter = counter+1;
            }
        }
    });

    // Insert time measurement statements
    for (const { path, label } of leafStatements) {
        const startTimer = parser.parse(`var t1_${label} = Date.now();`).program.body[0];
        const endTimer = parser.parse(`var t2_${label} = Date.now();`).program.body[0];
        const timeDiff = parser.parse(`print("${label}", t2_${label} - t1_${label});`).program.body[0];

        path.insertBefore(startTimer);

        const parentPath = path.parentPath;

        // Case 1: Loop body is a block and this is the last statement
        if (
            parentPath.isBlockStatement() &&
            Array.isArray(parentPath.node.body) &&
            parentPath.node.body[parentPath.node.body.length - 1] === path.node &&
            parentPath.parentPath &&
            (parentPath.parentPath.isForStatement() ||
            parentPath.parentPath.isWhileStatement() ||
            parentPath.parentPath.isDoWhileStatement())
        ) {
            // Safe to insert inside block
            const index = parentPath.node.body.indexOf(path.node);
            parentPath.node.body.splice(index + 1, 0, endTimer, timeDiff);
        }

        // Case 2: Loop body is NOT a block (e.g., for (...) stmt;)
        else if (
            (parentPath.isForStatement() ||
            parentPath.isWhileStatement() ||
            parentPath.isDoWhileStatement()) &&
            parentPath.get('body') === path
        ) {
            // Convert the single statement into a block
            const originalStmt = path.node;
            const block = t.blockStatement([
                originalStmt,
                endTimer,
                timeDiff
            ]);

            parentPath.node.body = block;
        }

        // Case 3: Normal insertAfter
        else {
            path.insertAfter(timeDiff);
            path.insertAfter(endTimer);
        }
    }

    const output = generator(ast, {}, code);
    process.stdout.write(`print("Total Instrumented:", ${counter});\n` + output.code);
});
