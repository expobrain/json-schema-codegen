// @flow

export class MyType {
  v: ?number;

  constructor(data: Object = {}) {
    this.v = data.v;
  }
}

export class Test {
  x: Array<MyType>;

  constructor(data: Object = {}) {
    this.x = Array.isArray(data.x) ? data.x.map((v) => MyType(v)) : [];
  }
}
