const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generate = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require('fs');

const args = process.argv.slice(2);

if (args.length < 2) {
    console.error("Usage: node delete_node.js <filename> <deleteIndices (comma-separated)>");
    process.exit(1);
}

const filename = args[0];
const deleteIndices = args[1].split(',').map(i => parseInt(i, 10)).filter(i => !isNaN(i));

console.log('/* deleteIndices:', deleteIndices, '*/');

function getStatementDepth(path) {
    let depth = 0;
    let parent = path.parentPath;

    while (parent) {
        if (parent.isBlockStatement()) {
            depth++;
        }
        parent = parent.parentPath;
    }

    return depth;
}

function processInput(filename, deleteIndices) {
    const code = fs.readFileSync(filename, 'utf-8');
    const ast = parser.parse(code, {
        sourceType: "module",
        plugins: ["jsx"]
    });

    let targetNodes = [];
    let index = 0;

    function collectNodes(path, depth) {
        if (depth === 1 || depth === 2) {
            targetNodes.push({ path, index });
            index++;
        }
    }

    traverse(ast, {
        enter(path) {
            if (
                path.isExpressionStatement() ||
                path.isVariableDeclaration() ||
                path.isIfStatement() ||
                path.isForStatement() ||
                path.isWhileStatement()
            ) {
                const depth = getStatementDepth(path);
                collectNodes(path, depth);
            }
        }
    });

    const toDeleteSet = new Set(deleteIndices);

    for (const { path, index } of targetNodes) {
        if (toDeleteSet.has(index)) {
            if (path.listKey && Array.isArray(path.parent[path.listKey])) {
                path.remove();
            } else if (t.isStatement(path.node)) {
                path.remove();
            } else {
                console.warn(`索引 ${index} 对应的节点不支持删除`);
            }
        }
    }

    const output = generate(ast, {}, code);
    console.log(output.code);
}

processInput(filename, deleteIndices);
