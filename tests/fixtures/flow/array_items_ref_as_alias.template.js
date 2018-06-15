// @flow

declare type MyType = string;

declare type Test = {
  x: Array<MyType>,

  constructor(data: ?Object): void
};
