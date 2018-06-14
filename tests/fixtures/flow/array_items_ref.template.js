declare type MyType = {
  v: ?number,

  constructor(data: ?Object): void
};

declare type Test = {
  x: Array<MyType>,

  constructor(data: ?Object): void
};
