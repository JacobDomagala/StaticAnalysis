const { make_dir_universal } = require('../index.js');

describe("make_dir_universal", () => {
  test("should replace backslashes with forward slashes", () => {
    const input = "C:\\Users\\John\\Documents\\file.txt";
    const expectedOutput = "C:/Users/John/Documents/file.txt";
    const actualOutput = make_dir_universal(input);
    expect(actualOutput).toEqual(expectedOutput);
  });

  test("should not change input if it already uses forward slashes", () => {
    const input = "/Users/John/Documents/file.txt";
    const expectedOutput = "/Users/John/Documents/file.txt";
    const actualOutput = make_dir_universal(input);
    expect(actualOutput).toEqual(expectedOutput);
  });
});