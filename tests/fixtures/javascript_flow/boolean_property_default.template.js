// @flow

export class Test {
  x: boolean;

  constructor(data: Object = {}) {
    this.x = typeof data.x === "boolean" ? data.x : true;
  }
}
