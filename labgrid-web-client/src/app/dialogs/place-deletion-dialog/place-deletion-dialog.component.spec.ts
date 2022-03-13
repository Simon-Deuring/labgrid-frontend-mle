import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlaceDeletionDialogComponent } from './place-deletion-dialog.component';

describe('PlaceDeletionDialogComponent', () => {
    let component: PlaceDeletionDialogComponent;
    let fixture: ComponentFixture<PlaceDeletionDialogComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [PlaceDeletionDialogComponent],
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(PlaceDeletionDialogComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
