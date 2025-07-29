def initialize_model(s_r_filepath = None, degree = 1, iterations = 100, n_s_values = 50, s_value_range_factor = [1 / 16, 1 / 8], *, weight_conv_window = 101, val_split = 0.5, s_value_increase = 1.05):
    import matplotlib.pyplot as plot
    import numpy
    import pandas

    plot.style.use('seaborn-v0_8-whitegrid')

    from scipy.interpolate import make_splrep
    from ExoRM import get_exorm_filepath, ExoRM, unique_radius, read_rm_data, preprocess_data, ForecasterRM

    data = read_rm_data()
    data = unique_radius(data)
    data = preprocess_data(data)

    x = data['radius']
    y = data['mass']

    x = numpy.log10(x)
    y = numpy.log10(y)

    w = numpy.diff(x)
    w = numpy.append(w, w[-1])

    window = weight_conv_window
    w = numpy.convolve(w, numpy.ones(window) / window, mode = 'same') # using edge-padding makes the edges have too much weight
    w *= 1 - (data['error_score'])
    w /= numpy.mean(w)

    n = len(x)
    s_values = numpy.linspace(n * s_value_range_factor[0], n * s_value_range_factor[1], n_s_values)

    split = 1 - val_split
    result = []

    def create_model_fast(x, y, w, s):
        model = make_splrep(x, y, k = degree, s = s, w = w)
        model = ExoRM(model, x, y)

        return model

    s_residuals = [] # (s, r)
    for _ in range(iterations):
        if _ % 10 == 9: print(f'Iteration {_ + 1}')

        mask = numpy.zeros(n, dtype = bool)
        i = numpy.sort(numpy.random.default_rng().choice(n, int(n * split), replace = False))
        mask[i] = True

        xt = x[mask]
        yt = y[mask]
        wt = w[mask]

        xv = x[~mask]
        yv = y[~mask]
        wv = w[~mask]

        best_s, best_wmae = numpy.inf, numpy.inf
        for s in s_values:
            model = create_model_fast(xt, yt, wt, s * split)
            wmae = numpy.mean(wv * (yv - model(xv)) ** 2)

            if wmae < best_wmae:
                best_wmae = wmae
                best_s = s

            s_residuals.append((s, wmae))

        result.append(best_s)

    best_s = numpy.mean(result) * s_value_increase
    print(f'Final s value ( * {s_value_increase} to prevent overfitting): {best_s}')

    if s_r_filepath is not None:
        pandas.DataFrame(s_residuals, columns = ['s_value', 'val_wmae']).to_csv(s_r_filepath, index = False)

    model = make_splrep(x, y, k = degree, s = best_s, w = w)
    model = ExoRM(model, x, y)
    model.add_best_s(best_s)
    model.create_error_model()

    x_smooth = numpy.linspace(min(x) - 0.1, max(x) + 0.1, 10000)
    y_smooth = model(x_smooth)

    y_smooth = model(x_smooth)
    e_smooth = model.error(x_smooth)

    plot.scatter(x, y, s = 1)
    plot.plot(x_smooth, y_smooth, color = 'C1')
    plot.plot(x_smooth, y_smooth + e_smooth, color = 'C2')
    plot.plot(x_smooth, y_smooth - e_smooth, color = 'C2')
    # plot.plot(x_smooth, e_smooth)
    plot.show()

    model.save(get_exorm_filepath('radius_mass_model.pkl'))

    return model