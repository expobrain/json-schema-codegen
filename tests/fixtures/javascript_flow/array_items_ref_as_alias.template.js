// @flow

export class Test {
  x: Array<MyType>;

  constructor(data: Object = {}) {
    this.x = Array.isArray(data.x) ? data.x : [];
  }
}
