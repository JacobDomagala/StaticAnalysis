const { make_dir_universal, check_for_exclude_dir } = require('../index.js');

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

describe('check_for_exclude_dir', () => {
  it('should return true if exclude_dir is empty', () => {
    const line = '/path/to/file.js';
    const exclude_dir = '';
    const result = check_for_exclude_dir(line, exclude_dir);
    expect(result).toBe(true);
  });

  it('should return false if line starts with exclude_dir', () => {
    const line = '/path/to/file.js';
    const exclude_dir = '/path/to';
    const result = check_for_exclude_dir(line, exclude_dir);
    expect(result).toBe(false);
  });

  it('should return false if line starts with exclude_dir', () => {
    const line = '/path/to/file.js';
    const exclude_dir = '/path/other';
    const result = check_for_exclude_dir(line, exclude_dir);
    expect(result).toBe(true);
  });
});