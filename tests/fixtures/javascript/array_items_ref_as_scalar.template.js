export class Test {
  x: Array<string>;

  constructor(data: Object = {}) {
    this.x = Array.isArray(data.x) ? data.x : [];
  }
}
