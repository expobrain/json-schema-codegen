// @flow

export class Test {
  x: ?boolean;

  constructor(data: Object = {}) {
    this.x = data.x;
  }
}
