import execjs


def build_ast(js_source_code: str):
    

    create_ast = execjs.compile("""
        // var esprima = require("esprima");
        var esprima = require("../EmbeddedFuzzer/node_modules/esprima");
        function readAST(code){
            var ast = {};
            ast = esprima.parseScript(code,{ loc: true });
            return ast;
        }        
    """)
    
    ast = create_ast.call("readAST", js_source_code)
    return ast


def generate_es_code(ast: dict):
    gen_es_code = execjs.compile("""
        // let escodegen = require('escodegen');
        let escodegen = require('../EmbeddedFuzzer/node_modules/escodegen');
        function genESCode(ast){
            let generated_code = escodegen.generate(ast);;
            return generated_code;
        }        
    """)
    code = gen_es_code.call("genESCode", ast)
    return code


def tokenize(js_source_code: str) -> list:

    split_into_token = execjs.compile("""
        // var esprima = require("esprima");
        var esprima = require("../EmbeddedFuzzer/node_modules/esprima");
        function tokenize(code){
            return esprima.tokenize(code);;
        }        
    """)
    return split_into_token.call("tokenize", js_source_code)

