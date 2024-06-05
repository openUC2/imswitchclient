import numpy as np
mImageToStageDisplacement = np.array(((
                -0.0012067713953994147,
                1.0026877733034147
),
            (
                -1.0026877733034136,
                0.0012067713954004155
            )))
mStageCoordinates = ((100,200))
mImageCoordinates = mImageToStageDisplacement*mStageCoordinates