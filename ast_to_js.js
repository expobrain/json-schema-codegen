// @flow

import fs from "fs";

import generate from "@babel/generator";

const generateOptions = {
  compact: false
};

const generateCode = (s: string): string => {
  const ast = JSON.parse(s);
  const { code } = generate(ast, generateOptions);

  return code;
};

if (process.stdin.isTTY) {
  // Executed as standalone
  if (process.argv.length < 4) {
    // eslint-disable-next-line no-console
    console.log("Usage: ast_to_js <input_ast_json> <output_js>");
    process.exit(1);
  }

  const inputAst = process.argv[2];
  const outputJs = process.argv[3];

  fs.readFile(inputAst, (err: ?Error, data: Buffer) => {
    if (err) {
      // eslint-disable-next-line no-console
      console.error(err);
      process.exit(1);
    }

    const code = generateCode(data.toString());

    fs.writeFile(outputJs, code, { encoding: "utf-8" }, (err: ?Error) => {
      if (err) {
        // eslint-disable-next-line no-console
        console.error(err);
        process.exit(1);
      }
    });
  });
} else {
  // Executed inside a pipe
  let buffer = "";

  process.stdin.setEncoding("utf8");

  process.stdin.on("readable", () => {
    const chunk = process.stdin.read();

    if (chunk !== null) {
      buffer += chunk.toString();
    }
  });

  process.stdin.on("end", () => {
    const code = generateCode(buffer);

    process.stdout.write(code);
  });
}
