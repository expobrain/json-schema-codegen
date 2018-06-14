export class Test {
  x: string;

  constructor(data: Object = {}) {
    this.x = typeof data.x === "string" ? data.x : "42";
  }
}
