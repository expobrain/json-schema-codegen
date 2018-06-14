export class Test {
  x: number;

  constructor(data: Object = {}) {
    this.x = Number.isInteger(data.x) ? data.x : 42;
  }
}
