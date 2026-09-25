fn main() {
    let w1 = -0.117767998417887e1;
    let w2 = 0.235573213359357e1;
    let w3 = 0.784513610477560e0;
    let w0 = 1.0 - 2.0 * (w1 + w2 + w3);
    let weights = [w3, w2, w1, w0, w1, w2, w3];
    println!("Weights initialized: {:?}", weights);
}