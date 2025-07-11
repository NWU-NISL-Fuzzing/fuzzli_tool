// Return variable names of variables used on specific lines

const esprima = require('esprima');
const fs = require('fs');

const filename = process.argv[2];
// 支持多个行号，例如：10,12,15
const targetLines = process.argv[3].split(',').map(Number);
const lineSet = new Set(targetLines);
// console.log(lineSet)

const code = fs.readFileSync(filename, 'utf-8');
const ast = esprima.parseScript(code, { loc: true, range: true });

const vars = new Set();

function visit(node) {
  if (!node || typeof node !== 'object') return;
  
  if (node.type === 'Identifier' && node.loc && lineSet.has(node.loc.start.line)) {
    vars.add(node.name);
  }

  for (const key in node) {
    if (Array.isArray(node[key])) {
      node[key].forEach(child => visit(child));
    } else {
      visit(node[key]);
    }
  }
}

visit(ast);
console.log([...vars]);
