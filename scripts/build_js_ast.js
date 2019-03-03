// @flow

import path from "path";
import fs from "fs";

import * as babylon from "babylon";

const BASE_AST_DIR = path.join(__dirname, "..", "tests", "fixtures");
const TEMPLATE_EXT = ".template.js";
const PRIMITIVES = ["boolean", "string", "number"];
const AST_LOCATION_KEYS = ["loc", "start", "end", "parenStart"];

const parserOptions = {
  sourceType: "module",
  plugins: ["flow"]
};

const removeLocationData = (obj: Object) => {
  return (
    Object.entries(obj)
      // eslint-disable-next-line no-unused-vars
      .filter(([key, value]) => !AST_LOCATION_KEYS.includes(key))
      .map(([key, value]) => {
        if (value !== null) {
          if (Array.isArray(value)) {
            value = value.map((v: any) => (PRIMITIVES.includes(typeof v) ? v : removeLocationData(v)));
          } else if (!PRIMITIVES.includes(typeof value)) {
            value = removeLocationData(((value: any): Object));
          }
        }

        return [key, value];
      })
      .reduce((acc, [key, value]) => {
        acc[key] = value;

        return acc;
      }, {})
  );
};

const buildAst = (astDir: string) => {
  fs.readdir(astDir, (err: ?Error, filenames: Array<string>) => {
    if (err) {
      throw err;
    }

    filenames
      .map(filename => path.join(astDir, filename))
      .filter(filename => filename.endsWith(TEMPLATE_EXT) && fs.statSync(filename).isFile())
      .forEach((filename: string) => {
        fs.readFile(filename, "utf8", (er: ?Error, sourceCode: string) => {
          const parsedAst = babylon.parse(sourceCode, parserOptions);
          const cleanAst = removeLocationData(parsedAst);

          const content = JSON.stringify(cleanAst, null, 2);
          const newFilename = path.join(astDir, path.basename(filename, TEMPLATE_EXT) + ".ast.json");

          // eslint-disable-next-line no-console
          console.log(`writing ${newFilename}`);

          fs.writeFile(newFilename, content, (err: ?Error) => {
            if (err) {
              throw err;
            }
          });
        });
      });
  });
};

["javascript_flow", "flow"].map(v => path.join(BASE_AST_DIR, v)).forEach(buildAst);
