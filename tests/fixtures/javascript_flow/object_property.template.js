// @flow

export class Test {
  x: ?Object;

  constructor(data: Object = {}) {
    this.x = data.x;
  }
}
