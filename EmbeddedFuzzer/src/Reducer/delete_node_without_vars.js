const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const generate = require("@babel/generator").default;
const t = require("@babel/types");
const fs = require('fs');

const args = process.argv.slice(2);

if (args.length < 3) {
    console.error("Usage: node delete_node.js <filename> <deleteIndices (comma-separated)> <vars (comma-separated)>");
    process.exit(1);
}

const filename = args[0];
const deleteIndices = args[1].split(',').map(i => parseInt(i, 10)).filter(i => !isNaN(i));
const protectedVars = new Set(args[2].split(',').map(s => s.trim()).filter(Boolean));

console.log('/* deleteIndices:', deleteIndices, '*/');
console.log('/* protectedVars:', protectedVars, '*/');

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

function containsProtectedVars(node) {
    let found = false;
    traverse(node, {
        Identifier(path) {
            if (protectedVars.has(path.node.name)) {
                found = true;
                path.stop();
            }
        }
    });
    return found;
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
            const node = path.node;
            const tmp_ast = {
                type: 'File',
                program: {
                    type: 'Program',
                    body: [node]
                }
            };

            const result = containsProtectedVars(tmp_ast);
            if (result) {
                console.log(`// 跳过删除索引 ${index}：包含受保护变量`);
                continue;
            }
            try {
                if (path.listKey && Array.isArray(path.parent[path.listKey])) {
                    console.log(`// 删除索引 ${index}`);
                    path.remove();
                } else if (t.isStatement(path.node)) {
                    console.log(`// 删除索引 ${index}`);
                    path.remove();
                } else {
                    console.log(`// 索引 ${index} 对应的节点不支持删除`);
                }                
            } catch (error) {
                console.error(`// 删除索引 ${index} 时发生错误：`, error);
            }
        }
    }

    const output = generate(ast, {}, code);
    console.log(output.code);
}

processInput(filename, deleteIndices);
