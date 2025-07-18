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

function isLeafStatement(path) {
    if (!path.isStatement()) return false;
    if (path.isReturnStatement()) return false;

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

function processInput(filename, deleteIndices) {
    const code = fs.readFileSync(filename, 'utf-8');
    const ast = parser.parse(code, {
        sourceType: "module",
        plugins: ["jsx"]
    });

    let targetNodes = [];
    let index = 0;

    traverse(ast, {
        enter(path) {
            if (isLeafStatement(path)) {
                targetNodes.push({ path, index });
                index++;
            }
        }
    });

    const toDeleteSet = new Set(deleteIndices);

    for (const { path, index } of targetNodes) {
        if (toDeleteSet.has(index)) {
            try{
                if (path.listKey && Array.isArray(path.parent[path.listKey])) {
                    path.remove();
                } else if (t.isStatement(path.node)) {
                    path.remove();
                } else {
                    console.warn(`索引 ${index} 对应的节点不支持删除`);
                }
            } catch (e) {
                console.error(`Error while deleting node at index ${index}:`, e);
            }
        }
    }

    const output = generate(ast, {}, code);
    console.log(output.code);
}

processInput(filename, deleteIndices);
