// @flow

export class Test {
  x: ?number;

  constructor(data: Object = {}) {
    this.x = data.x;
  }
}
