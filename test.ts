function greet(name: string): number {  // Wrong return type
    return "Hello " + name;  // Returns string, not number
}

const result: string = greet(42);  // Wrong arg type
console.log(result);
