use pyo3::prelude::*;
extern crate nalgebra as na;
use na::{DMatrix};
use std::f64::consts::PI;
use libm::{atan2,sin,cos,log,sqrt};


fn solve_rs(airfoil_coords: &Vec<Vec<f64>>, alpha_deg: f64) -> (Vec<Vec<f64>>, Vec<f64>, f64) {
    // Number of points
    let n = airfoil_coords.len(); // Number of panel end points
    let m = n - 1; // Number of control points

    // Initialize arrays
    let mut ep: DMatrix<f64> = DMatrix::<f64>::zeros(n, 2); // Clockwise-defined panel end points
    let mut ept: DMatrix<f64> = DMatrix::<f64>::zeros(n, 2); // End points from file
    let mut pt1: DMatrix<f64> = DMatrix::<f64>::zeros(m, 2); // Start point of panel
    let mut pt2: DMatrix<f64> = DMatrix::<f64>::zeros(m, 2); // End point of panel
    let mut co: DMatrix<f64> = DMatrix::<f64>::zeros(m, 2); // Collocation point
    let mut co_out: Vec<Vec<f64>> = vec![vec![0.0; 2]; m]; // Collocation point (return format)
    let mut cp: Vec<f64> = vec![0.0; m]; // Surface pressure coefficient
    let mut a: DMatrix<f64> = DMatrix::<f64>::zeros(n, n); // Aerodynamic influence coefficient matrix
    let mut b: DMatrix<f64> = DMatrix::<f64>::zeros(n, n); // Tangential induced velocities (with gammas)
    let mut th: DMatrix<f64> = DMatrix::<f64>::zeros(m, 1); // Panel angle
    let mut dl: DMatrix<f64> = DMatrix::<f64>::zeros(m, 1); // Panel length
    let mut rhs: DMatrix<f64> = DMatrix::<f64>::zeros(n, 1); // Freestream component normal to panel
    let mut v: DMatrix<f64> = DMatrix::<f64>::zeros(m, 1); // Panel tangential velocity

    // Initialize floats
    let mut xt: f64;
    let mut zt: f64;
    let mut x2t: f64;
    let mut z2t: f64;
    let mut x: f64;
    let mut z: f64;
    let mut x2: f64;
    let mut r1: f64;
    let mut r2: f64;
    let mut th1: f64;
    let mut th2: f64;
    let mut u1l: f64;
    let mut u2l: f64;
    let mut w1l: f64;
    let mut w2l: f64;
    let mut u1: f64;
    let mut u2: f64;
    let mut w1: f64;
    let mut w2: f64;
    let mut hold_a: f64 = 0.0;
    let mut hold_b: f64 = 0.0;

    // Angle of attack in radians
    let al = alpha_deg * PI / 180.0;

    // Read in x/c and y/c panel end point positions from airfoil coordinates
    for i in 0..n {
        ept[(i, 0)] = airfoil_coords[i][0];
        ept[(i, 1)] = airfoil_coords[i][1];
    }
    
    // Order panel end points defined in clockwise direction
    for i in 0..n {
        ep[(i, 0)] = ept[(n-i-1, 0)];
        ep[(i, 1)] = ept[(n-i-1, 1)];
    }

    // Define end points of each panel (pt1 is start, pt2 is end)
    for i in 0..m {
        pt1[(i, 0)] = ep[(i, 0)];
        pt2[(i, 0)] = ep[(i+1, 0)];
        pt1[(i, 1)] = ep[(i, 1)];
        pt2[(i, 1)] = ep[(i+1, 1)];
    }

    // Determine local slope of each panel
    let mut dz: f64;
    let mut dx: f64;
    for i in 0..m {
        dz = pt2[(i, 1)] - pt1[(i, 1)];
        dx = pt2[(i, 0)] - pt1[(i, 0)];
        th[i] = atan2(dz, dx);
    }

    // Identify collocation points for each panel (half-panel location)
    for i in 0..m {
        co[(i, 0)] = (pt2[(i, 0)] - pt1[(i, 0)]) / 2.0 + pt1[(i, 0)];
        co[(i, 1)] = (pt2[(i, 1)] - pt1[(i, 1)]) / 2.0 + pt1[(i, 1)];
        co_out[i][0] = co[(i, 0)];
        co_out[i][1] = co[(i, 1)];
    }

    // Determine influence coefficients
    for i in 0..m {
        for j in 0..m {
            // Determine location of collocation point i in terms of panel j coordinates
            xt = co[(i, 0)] - pt1[(j, 0)];
            zt = co[(i, 1)] - pt1[(j, 1)];
            x2t = pt2[(j, 0)] - pt1[(j, 0)];
            z2t = pt2[(j, 1)] - pt1[(j, 1)];
            
            x = xt * cos(th[(j, 0)]) + zt * sin(th[(j, 0)]);
            z = -xt * sin(th[(j, 0)]) + zt * cos(th[(j, 0)]);
            x2 = x2t * cos(th[(j, 0)]) + z2t * sin(th[(j, 0)]);

            // Store each length of each panel (only required for first loop in i)
            if i == 0 {
                dl[(j, 0)] = x2;
            }

            // Determine radial distance and angle between corner points of jth
            // panel and ith control point
            r1 = sqrt(x.powf(2.0) + z.powf(2.0));
            r2 = sqrt((x - x2).powf(2.0) + z.powf(2.0));
            th1 = atan2(z, x);
            th2 = atan2(z, x - x2);

            // Determine influence of jth panel on ith control point
            // (include consideration for self-induced velocities)
            if i == j {
                u1l = -0.5 * (x - x2) / x2;
                u2l = 0.5 * x / x2;
                w1l = -0.15916;
                w2l = -w1l;
            } else {
                u1l = -(z * log(r2 / r1) + x * (th2 - th1) - x2 * (th2 - th1)) / (2.0 * PI * x2);
                u2l = (z * log(r2 / r1) + x * (th2 - th1)) / (2.0 * PI * x2);
                w1l = -((x2 - z * (th2 - th1)) - x * log(r1 / r2) + x2 * log(r1 / r2)) / (2.0 * PI * x2);
                w2l = ((x2 - z * (th2 - th1)) - x * log(r1 / r2)) / (2.0 * PI * x2);
            }
            
            // Rotate coordinates back from jth panel reference frame to
            // airfoil chord frame
            u1 = u1l * cos(-th[(j, 0)]) + w1l * sin(-th[(j, 0)]);
            u2 = u2l * cos(-th[(j, 0)]) + w2l * sin(-th[(j, 0)]);
            w1 = -u1l * sin(-th[(j, 0)]) + w1l * cos(-th[(j, 0)]);
            w2 = -u2l * sin(-th[(j, 0)]) + w2l * cos(-th[(j, 0)]);

            // Define AIC: a(i, j) is the component of velocity normal to control
            // point i due to panel j
            // b(i, j) is the tangential velocity along control point i due to
            // panel j, used after solving for gammas
            if j == 0 {
                a[(i, 0)] = -u1 * sin(th[(i, 0)]) + w1 * cos(th[(i, 0)]);
                hold_a = -u2 * sin(th[(i, 0)]) + w2 * cos(th[(i, 0)]);
                b[(i, 0)] = u1 * cos(th[(i, 0)]) + w1 * sin(th[(i, 0)]);
                hold_b = u2 * cos(th[(i, 0)]) + w2 * sin(th[(i, 0)]);
            } else if j == m - 1 {
                a[(i, m - 1)] = -u1 * sin(th[(i, 0)]) + w1 * cos(th[(i, 0)]) + hold_a;
                a[(i, n - 1)] = -u2 * sin(th[(i, 0)]) + w2 * cos(th[(i, 0)]);
                b[(i, m - 1)] = u1 * cos(th[(i, 0)]) + w1 * sin(th[(i, 0)]) + hold_b;
                b[(i, n - 1)] = u2 * cos(th[(i, 0)]) + w2 * sin(th[(i, 0)]);
            } else {
                a[(i, j)] = -u1 * sin(th[(i, 0)]) + w1 * cos(th[(i, 0)]) + hold_a;
                hold_a = -u2 * sin(th[(i, 0)]) + w2 * cos(th[(i, 0)]);
                b[(i, j)] = u1 * cos(th[(i, 0)]) + w1 * sin(th[(i, 0)]) + hold_b;
                hold_b = u2 * cos(th[(i, 0)]) + w2 * sin(th[(i, 0)]);
            }
        }
        
        // Set up freestream component of boundary condition
        rhs[(i, 0)] = cos(al) * sin(th[(i, 0)]) - sin(al) * cos(th[(i, 0)]);
    }

    // Enforce Kutta condition
    rhs[(n-1, 0)] = 0.0;

    a[(n-1, 0)] = 1.0;
    a[(n-1, n-1)] = 1.0;

    // Invert "a" matrix to solve for gammas
    let a_inv: DMatrix<f64> = a.try_inverse().expect("Matrix should be invertible");
    let g: DMatrix<f64> = a_inv * rhs;

    // With known gammas, solve for Cl, Cps
    let mut cl: f64 = 0.0;
    let mut vel: f64;
    for i in 0..m {
        vel = 0.0;
        for j in 0..n {
            vel = vel + (b[(i, j)] * g[(j, 0)]);
        }
        v[(i, 0)] = vel + cos(al) * cos(th[(i, 0)]) + sin(al) * sin(th[(i, 0)]);
        cl = cl + ((g[(i, 0)] + g[(i+1, 0)]) * dl[(i, 0)]);
    }
    for i in 0..m {
        cp[i] = 1.0 - v[(i, 0)].powf(2.0);
    }

    // Return the result
    (co_out, cp, cl)
}


#[pyfunction]
fn solve(airfoil_coords: Vec<Vec<f64>>, alpha_deg: f64) -> (Vec<Vec<f64>>, Vec<f64>, f64) {
    return solve_rs(&airfoil_coords, alpha_deg);
}


#[pyfunction]
fn sweep_alpha(airfoil_coords: Vec<Vec<f64>>, alpha_deg: Vec<f64>) -> (Vec<Vec<Vec<f64>>>, Vec<Vec<f64>>, Vec<f64>) {
    let mut co_list: Vec<Vec<Vec<f64>>> = Vec::new();
    let mut cp_list: Vec<Vec<f64>> = Vec::new();
    let mut cl_list: Vec<f64> = Vec::new();
    for alpha in alpha_deg.into_iter() {
        let analysis_result = solve_rs(&airfoil_coords, alpha);
        co_list.push(analysis_result.0);
        cp_list.push(analysis_result.1);
        cl_list.push(analysis_result.2);
    }

    // Return the result
    (co_list, cp_list, cl_list)
}


#[pymodule]
fn lsv_panel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve, m)?)?;
    m.add_function(wrap_pyfunction!(sweep_alpha, m)?)?;
    Ok(())
}
