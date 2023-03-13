const fs = require('fs');
const core = require('@actions/core');

const { make_dir_universal, check_for_exclude_dir, get_line_info, get_line_end } = require('../index.js');


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

describe('get_line_end', () => {
  const mockCoreInput = jest.spyOn(core, 'getInput');
  mockCoreInput.mockReturnValue(10);

  test('returns correct line end', () => {
    const filePath = '/path/to/file.txt';
    const lineStart = 10;
    const expectedLineEnd = '20';

    const mockReadFileSync = jest.spyOn(fs, 'readFileSync');
    mockReadFileSync.mockReturnValue(`${'\n'.repeat(50)}`);

    const result = get_line_end(filePath, lineStart);
    expect(result).toEqual(expectedLineEnd);
    expect(mockCoreInput).toHaveBeenCalledWith('num_lines_to_display');
  });

  test('returns correct line end when num_lines_to_display is larger than file length', () => {
    const filePath = '/path/to/file.txt';
    const lineStart = 10;
    const expectedLineEnd = '12';

    const mockReadFileSync = jest.spyOn(fs, 'readFileSync');
    mockReadFileSync.mockReturnValue(`${'\n'.repeat(12)}`);

    const result = get_line_end(filePath, lineStart);
    expect(result).toEqual(expectedLineEnd);
    expect(mockCoreInput).toHaveBeenCalledWith('num_lines_to_display');
  });
});

describe('get_line_info', () => {
  const mockCoreInput = jest.spyOn(core, 'getInput');
  mockCoreInput.mockReturnValue("10");

  it('should return expected line info for GCC', () => {
    const compiler = "GCC";
    const line = "/path/to/file.c:123:45: error: foo";

    const mockReadFileSync = jest.spyOn(fs, 'readFileSync');
    mockReadFileSync.mockReturnValue(`${'\n'.repeat(123)}`);

    const result = get_line_info(compiler, line);
    expect(result).toEqual(['/path/to/file.c', '123', '123', 'error']);
    expect(mockCoreInput).toHaveBeenCalledWith('num_lines_to_display');
  });

  it('should return expected line info for Clang', () => {
    const compiler = "Clang";
    const line = "/path/to/file.c:123:45: error: foo";

    const mockReadFileSync = jest.spyOn(fs, 'readFileSync');
    mockReadFileSync.mockReturnValue(`${'\n'.repeat(127)}`);

    const result = get_line_info(compiler, line);
    expect(result).toEqual(['/path/to/file.c', '123', '127', 'error']);
    expect(mockCoreInput).toHaveBeenCalledWith('num_lines_to_display');
  });

  it('should return expected line info for MSVC', () => {
    const compiler = "MSVC";
    const line = "C:\\path\\to\\file.cpp(123): warning C420";

    const mockReadFileSync = jest.spyOn(fs, 'readFileSync');
    mockReadFileSync.mockReturnValue(`${'\n'.repeat(210)}`);

    const result = get_line_info(compiler, line);
    expect(result).toEqual(['C:\\path\\to\\file.cpp', '123', '133', 'warning']);
    expect(mockCoreInput).toHaveBeenCalledWith('num_lines_to_display');
  });
});